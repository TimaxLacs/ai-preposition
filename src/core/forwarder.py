import logging
import os
from dotenv import load_dotenv
from ..providers.telegram.client import TelegramProvider
from ..providers.vk.client import VKProvider

logger = logging.getLogger(__name__)
load_dotenv()

class Forwarder:
    def __init__(self, telegram_provider: TelegramProvider, vk_provider: VKProvider):
        self.telegram = telegram_provider
        self.vk = vk_provider
        
        # Каналы по умолчанию
        self.default_tg_channel = os.getenv("TELEGRAM_OUTPUT_CHANNEL")
        self.default_vk_group = os.getenv("VK_OUTPUT_GROUP_ID")

    async def forward(self, post_data: dict, filter_result: dict) -> bool:
        """
        Пересылает пост в целевые каналы
        """
        success = False
        
        # Формируем текст с результатами
        extra_text = (
            f"📌 Категория: **{filter_result.category}**\n"
            f"🔍 Уверенность: **{filter_result.confidence:.0%}**\n"
            f"💭 {filter_result.reason}\n"
            f"📍 Источник: {post_data.get('source_name', 'Unknown')}"
        )
        
        # 1. Отправка в Telegram
        if self.default_tg_channel:
            # Для Telegram используем нативный forward, если источник Telegram
            if post_data['source_type'] == 'telegram' and post_data.get('raw_object'):
                tg_success = await self.telegram.forward_message(
                    self.default_tg_channel, 
                    post_data['raw_object'],
                    extra_text
                )
            else:
                # Если источник не Telegram, просто шлем текст
                # TODO: реализовать send_message в провайдере для простого текста
                # Пока используем forward_message который требует message_obj, 
                # но для кросс-постинга нужно доработать провайдеры.
                # В рамках текущей задачи предположим, что кросс-постинг пока ограничен
                logger.warning("Cross-posting logic needs enhancement for raw text sending")
                tg_success = False 
                
            if tg_success:
                success = True

        # 2. Отправка в VK
        if self.default_vk_group and self.vk.is_running:
            # Для VK всегда создаем новый пост
            vk_success = await self.vk.forward_message(
                self.default_vk_group,
                post_data.get('raw_object', {'text': post_data['text'], 'owner_id': post_data['source_id'], 'id': post_data['post_id']}),
                extra_text
            )
            if vk_success:
                success = True
                
        return success





