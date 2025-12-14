from abc import ABC, abstractmethod
from typing import Callable, Any, List

class BaseProvider(ABC):
    """Базовый абстрактный класс для провайдеров соцсетей"""

    @abstractmethod
    async def start(self):
        """Запуск провайдера и авторизация"""
        pass

    @abstractmethod
    async def stop(self):
        """Остановка провайдера"""
        pass
    
    @abstractmethod
    async def monitor_channels(self, channels: List[str], callback: Callable):
        """
        Запуск мониторинга каналов
        
        Args:
            channels: Список ID/юзернеймов каналов
            callback: Функция, которая будет вызываться при новом посте
        """
        pass
        
    @abstractmethod
    async def forward_message(self, target_id: str, message_obj: Any, extra_text: str = ""):
        """Пересылка сообщения в целевой канал"""
        pass





