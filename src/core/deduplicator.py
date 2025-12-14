import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..storage.models import ProcessedPost
from ..storage.cache import cache
from ..utils.helpers import get_post_hash

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_duplicate(self, source_id: str, post_id: str, text: str) -> bool:
        """
        Проверяет, был ли пост уже обработан.
        Проверка идет по ID поста (в рамках источника) и по хешу текста (глобально).
        """
        # 1. Проверка в кэше по ID (быстрая)
        cache_key_id = f"processed:id:{source_id}:{post_id}"
        if await cache.exists(cache_key_id):
            logger.debug(f"Duplicate found in cache by ID: {post_id}")
            return True
            
        # 2. Проверка в кэше по хешу текста (если включено)
        text_hash = get_post_hash(text)
        cache_key_hash = f"processed:hash:{text_hash}"
        if await cache.exists(cache_key_hash):
            logger.debug(f"Duplicate found in cache by hash: {text_hash}")
            return True
            
        # 3. Проверка в БД (если нет в кэше)
        # Проверяем ID
        query = select(ProcessedPost).where(
            ProcessedPost.source_id == source_id,
            ProcessedPost.post_id == post_id
        )
        result = await self.session.execute(query)
        if result.scalar_one_or_none():
            # Восстанавливаем в кэше
            await cache.set(cache_key_id, "1", ttl=86400)
            return True
            
        # Проверяем хеш
        query = select(ProcessedPost).where(ProcessedPost.text_hash == text_hash)
        result = await self.session.execute(query)
        if result.scalar_one_or_none():
            await cache.set(cache_key_hash, "1", ttl=86400)
            return True
            
        return False

    async def mark_processed(self, source_type: str, source_id: str, post_id: str, text: str, 
                           filter_result: dict = None, was_forwarded: bool = False):
        """Сохраняет пост как обработанный"""
        text_hash = get_post_hash(text)
        
        # Сохраняем в БД
        processed_post = ProcessedPost(
            source_type=source_type,
            source_id=source_id,
            post_id=post_id,
            text_hash=text_hash,
            filter_result=filter_result,
            category=filter_result.get('category') if filter_result else None,
            confidence=filter_result.get('confidence') if filter_result else None,
            was_forwarded=was_forwarded
        )
        self.session.add(processed_post)
        await self.session.commit()
        
        # Сохраняем в кэш
        await cache.set(f"processed:id:{source_id}:{post_id}", "1", ttl=86400)
        await cache.set(f"processed:hash:{text_hash}", "1", ttl=86400)





