import os
import asyncio
from typing import List, Callable, Any
from telethon import TelegramClient, events
from telethon.tl.types import Message
from ..base import BaseProvider
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class TelegramProvider(BaseProvider):
    def __init__(self):
        self.api_id = int(os.getenv("TELEGRAM_API_ID", 0))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.client = TelegramClient('ai_filter_session', self.api_id, self.api_hash)
        self.callback = None
        
    async def start(self):
        logger.info("Starting Telegram Provider...")
        try:
            await self.client.start(phone=self.phone)
            me = await self.client.get_me()
            logger.info(f"Telegram connected as {me.username}")
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}")
            raise

    async def stop(self):
        logger.info("Stopping Telegram Provider...")
        await self.client.disconnect()

    async def monitor_channels(self, channels: List[str], callback: Callable):
        """
        Начинает слушать указанные каналы.
        """
        self.callback = callback
        
        # Нормализация имен каналов (обеспечиваем int или str)
        entity_ids = []
        for ch in channels:
            try:
                # Пытаемся преобразовать в int если это ID
                if ch.lstrip('-').isdigit():
                    entity_ids.append(int(ch))
                else:
                    entity_ids.append(ch)
            except ValueError:
                entity_ids.append(ch)
                
        logger.info(f"Monitoring Telegram channels: {entity_ids}")

        @self.client.on(events.NewMessage(chats=entity_ids))
        async def handler(event):
            try:
                # Преобразуем event.message в нашу структуру или передаем как есть
                # Для гибкости передаем сырое сообщение + метаданные
                message = event.message
                text = message.text or message.message or ""
                
                # Игнорируем пустые сообщения (хотя могут быть медиа)
                if not text and not message.media:
                    return

                # Получаем инфо о канале
                chat = await event.get_chat()
                source_id = str(chat.id)
                source_name = getattr(chat, 'username', getattr(chat, 'title', 'Unknown'))
                
                post_data = {
                    "source_type": "telegram",
                    "source_id": source_id,
                    "source_name": source_name,
                    "post_id": str(message.id),
                    "text": text,
                    "raw_object": message,  # Сохраняем объект для пересылки
                    "media": bool(message.media)
                }
                
                if self.callback:
                    await self.callback(post_data)
                    
            except Exception as e:
                logger.error(f"Error handling Telegram message: {e}")

    async def forward_message(self, target_id: str, message_obj: Any, extra_text: str = ""):
        """
        Пересылает сообщение.
        target_id: куда слать (@channel или ID)
        message_obj: объект сообщения Telethon
        extra_text: текст, который нужно добавить (например, результат анализа)
        """
        try:
            # Telethon умеет принимать int ID или username str
            target = int(target_id) if target_id.lstrip('-').isdigit() else target_id
            
            # Пересылаем сообщение
            # Используем send_message с forward, или forward_messages
            # forward_messages предпочтительнее для сохранения авторства
            await self.client.forward_messages(entity=target, messages=message_obj)
            
            # Если есть доп. текст (комментарий с категорией), шлем следом
            if extra_text:
                await self.client.send_message(entity=target, message=extra_text)
                
            logger.info(f"Message forwarded to {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to forward message to {target_id}: {e}")
            return False





