import os
import asyncio
import logging
from typing import List, Callable, Any
from ..base import BaseProvider
from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType

logger = logging.getLogger(__name__)
load_dotenv()

class VKProvider(BaseProvider):
    def __init__(self):
        self.token = os.getenv("VK_TOKEN")
        self.vk_session = None
        self.vk = None
        self.longpoll = None
        self.is_running = False
        self.callback = None
        
    async def start(self):
        logger.info("Starting VK Provider...")
        if not self.token:
            logger.warning("VK_TOKEN not set, VK provider disabled")
            return

        try:
            self.vk_session = vk_api.VkApi(token=self.token)
            self.vk = self.vk_session.get_api()
            # Проверка авторизации
            user = self.vk.users.get()
            logger.info(f"VK connected as user ID: {user[0]['id']}")
            self.is_running = True
        except Exception as e:
            logger.error(f"Failed to start VK client: {e}")
            self.is_running = False
            # Не рейзим ошибку, чтобы приложение могло работать без VK

    async def stop(self):
        logger.info("Stopping VK Provider...")
        self.is_running = False

    async def monitor_channels(self, channels: List[str], callback: Callable):
        """
        Для VK мониторинг реализован через периодический опрос (polling), 
        так как LongPoll для пользователя требует сложных настроек, 
        а Bot LongPoll работает только для сообществ.
        
        Здесь мы будем использовать простой polling последних постов.
        """
        if not self.is_running:
            return

        self.callback = callback
        logger.info(f"Starting VK polling for groups: {channels}")

        # Запускаем задачу опроса в фоне
        asyncio.create_task(self._poll_loop(channels))

    async def _poll_loop(self, groups: List[str]):
        """Цикл опроса групп"""
        last_posts = {}  # {group_id: last_post_id}

        while self.is_running:
            for group in groups:
                try:
                    # Преобразуем ID группы (если передана ссылка или имя)
                    # vk_api обычно принимает domain или id
                    domain = group.replace('https://vk.com/', '').replace('public', '').replace('club', '')
                    if domain.startswith('-'):
                        domain = domain[1:] # Убираем минус если есть

                    # Получаем последний пост
                    # Используем run_in_executor т.к. vk_api синхронный
                    posts = await asyncio.to_thread(
                        self.vk.wall.get, domain=domain, count=2
                    )
                    
                    if not posts or not posts['items']:
                        continue

                    # Берем самый свежий пост (не закрепленный)
                    items = posts['items']
                    post = items[0]
                    if post.get('is_pinned') and len(items) > 1:
                        post = items[1]

                    post_id = f"{post['owner_id']}_{post['id']}"
                    
                    # Если пост новый
                    if group not in last_posts:
                        last_posts[group] = post_id
                        continue # Первый запуск - просто запоминаем
                    
                    if last_posts[group] != post_id:
                        last_posts[group] = post_id
                        
                        # Формируем данные
                        post_data = {
                            "source_type": "vk",
                            "source_id": str(post['owner_id']),
                            "source_name": group,
                            "post_id": post_id,
                            "text": post.get('text', ''),
                            "raw_object": post,
                            "media": bool(post.get('attachments'))
                        }
                        
                        if self.callback:
                            await self.callback(post_data)
                            
                except Exception as e:
                    logger.error(f"Error polling VK group {group}: {e}")
            
            # Ждем перед следующим опросом (чтобы не словить rate limit)
            await asyncio.sleep(60) 

    async def forward_message(self, target_id: str, message_obj: Any, extra_text: str = ""):
        """
        Публикация поста на стену или в ЛС.
        Для VK "пересылка" сложнее, обычно это репост или копирование текста.
        Мы будем копировать текст и прикладывать ссылку на оригинал.
        """
        if not self.is_running:
            return False

        try:
            # message_obj здесь это dict от VK API
            original_text = message_obj.get('text', '')
            original_link = f"https://vk.com/wall{message_obj['owner_id']}_{message_obj['id']}"
            
            final_text = f"{extra_text}\n\n{original_text}\n\nИсточник: {original_link}"
            
            target = int(target_id)
            
            # Публикация на стене (если target < 0 это группа)
            await asyncio.to_thread(
                self.vk.wall.post,
                owner_id=target,
                message=final_text
            )
            
            logger.info(f"Posted to VK {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to post to VK {target_id}: {e}")
            return False





