import json
import os
from typing import Optional, Any, Union
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"


class Cache:
    """Обертка над Redis для кэширования"""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._local_cache: dict = {}  # Fallback for dev without Redis

    async def connect(self):
        """Инициализация подключения"""
        if REDIS_ENABLED:
            self._redis = redis.from_url(REDIS_URL, decode_responses=True)
            try:
                await self._redis.ping()
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}. Switching to local cache.")
                self._redis = None

    async def close(self):
        """Закрытие соединения"""
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения по ключу"""
        if self._redis:
            try:
                value = await self._redis.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            except Exception:
                return None
        return self._local_cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Установка значения
        ttl: время жизни в секундах
        """
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        if self._redis:
            try:
                await self._redis.set(key, value_str, ex=ttl)
            except Exception:
                pass
        else:
            self._local_cache[key] = value  # Local cache doesn't support TTL implementation easily

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        if self._redis:
            return await self._redis.exists(key) > 0
        return key in self._local_cache

    async def delete(self, key: str):
        """Удаление ключа"""
        if self._redis:
            await self._redis.delete(key)
        elif key in self._local_cache:
            del self._local_cache[key]

# Глобальный инстанс кэша
cache = Cache()





