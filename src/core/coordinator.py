import asyncio
import logging
from typing import List
from ..providers.telegram.client import TelegramProvider
from ..providers.vk.client import VKProvider
from ..ai.client import AIClient
from ..filters.engine import FilterEngine
from ..storage.database import async_session_maker
from .processor import PostProcessor
from .forwarder import Forwarder
from ..storage.repositories.sources import SourceRepository

logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self):
        # Инициализация компонентов
        self.telegram = TelegramProvider()
        self.vk = VKProvider()
        
        # AI клиент (заглушка пока что)
        self.ai_client = AIClient()
        self.filter_engine = FilterEngine(self.ai_client)
        
        self.forwarder = Forwarder(self.telegram, self.vk)
        
        self.is_running = False

    async def _handle_new_post(self, post_data: dict):
        """Callback для новых постов от провайдеров"""
        # Создаем новую сессию для каждого запроса
        async with async_session_maker() as session:
            processor = PostProcessor(session, self.filter_engine, self.forwarder)
            try:
                await processor.process_post(post_data)
            except Exception as e:
                logger.exception(f"Error processing post: {e}")

    async def start(self):
        """Запуск всей системы"""
        self.is_running = True
        logger.info("Starting Coordinator...")
        
        # 1. Запуск провайдеров
        await self.telegram.start()
        await self.vk.start()
        
        # 2. Получение списка каналов для мониторинга из БД
        async with async_session_maker() as session:
            repo = SourceRepository(session)
            sources = await repo.list_enabled()
            
            tg_channels = [s.source_id for s in sources if s.type == 'telegram']
            vk_groups = [s.source_id for s in sources if s.type == 'vk']
            
        logger.info(f"Loaded {len(tg_channels)} Telegram channels and {len(vk_groups)} VK groups from DB")
            
        # 3. Запуск мониторинга
        if tg_channels:
            await self.telegram.monitor_channels(tg_channels, self._handle_new_post)
            
        if vk_groups:
            await self.vk.monitor_channels(vk_groups, self._handle_new_post)
            
        # 4. Бесконечный цикл ожидания (или ожидание сигнала остановки)
        logger.info("System is running. Press Ctrl+C to stop.")
        while self.is_running:
            await asyncio.sleep(1)

    async def stop(self):
        """Остановка системы"""
        self.is_running = False
        await self.telegram.stop()
        await self.vk.stop()
        logger.info("Coordinator stopped.")





