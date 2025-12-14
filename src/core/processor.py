import logging
from sqlalchemy.ext.asyncio import AsyncSession
from ..filters.engine import FilterEngine
from ..storage.repositories.sources import SourceRepository
from .deduplicator import Deduplicator
from .forwarder import Forwarder

logger = logging.getLogger(__name__)

class PostProcessor:
    def __init__(self, session: AsyncSession, filter_engine: FilterEngine, forwarder: Forwarder):
        self.session = session
        self.filter_engine = filter_engine
        self.forwarder = forwarder
        self.deduplicator = Deduplicator(session)
        self.source_repo = SourceRepository(session)

    async def process_post(self, post_data: dict):
        """
        Основной пайплайн обработки поста
        """
        source_id = post_data['source_id']
        post_id = post_data['post_id']
        text = post_data['text']
        
        # 1. Проверка на дубликаты
        if await self.deduplicator.is_duplicate(source_id, post_id, text):
            logger.debug(f"Skipping duplicate post {post_id} from {source_id}")
            return

        # 2. Получение настроек источника и фильтров
        # Ищем источник в БД по source_id (ID канала/группы)
        source = await self.source_repo.get_by_source_id(source_id)
        
        if not source:
            # Если источника нет в БД, значит он не настроен или новый
            # Можно либо пропускать, либо использовать дефолтные фильтры
            # В MVP мы пропускаем
            logger.debug(f"Source {source_id} not found in DB configuration")
            # Для теста пропустим, но в реальности нужно добавить источник в БД
            return
            
        if not source.enabled:
            return

        if not source.filters:
            logger.debug(f"No filters configured for source {source_id}")
            return

        # 3. Применение фильтров
        logger.info(f"Analyzing post {post_id} from {source.name or source_id}...")
        
        filter_result = await self.filter_engine.apply_filters(text, source.filters)
        
        was_forwarded = False
        
        # 4. Обработка результата
        if filter_result:
            logger.info(f"✅ Post matched filter '{filter_result.filter_id}' (confidence: {filter_result.confidence:.2f})")
            
            # 5. Пересылка
            was_forwarded = await self.forwarder.forward(post_data, filter_result)
        else:
            logger.info(f"❌ Post rejected")

        # 6. Сохранение результата (маркировка как обработанного)
        await self.deduplicator.mark_processed(
            source_type=post_data['source_type'],
            source_id=source_id,
            post_id=post_id,
            text=text,
            filter_result=filter_result.to_dict() if filter_result else None,
            was_forwarded=was_forwarded
        )





