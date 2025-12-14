import asyncio
import json
import random
from typing import Dict, Optional, Any
from .prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class AIClient:
    """
    Клиент для взаимодействия с AI API.
    Текущая реализация: ЗАГЛУШКА (MOCK)
    """
    
    def __init__(self, provider: str = "groq", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        
    async def analyze_post(self, text: str, filters_config: dict) -> Dict[str, Any]:
        """
        Анализирует пост на основе переданных фильтров.
        
        Args:
            text: Текст поста
            filters_config: Конфигурация фильтра (промпт, категории и т.д.)
            
        Returns:
            Dict с результатом анализа
        """
        # Имитация задержки сети
        await asyncio.sleep(0.5)
        
        # --- MOCK LOGIC ---
        # Простая эвристика для имитации AI, чтобы тесты проходили логично
        text_lower = text.lower()
        
        is_relevant = False
        category = "Other"
        confidence = 0.0
        reason = "Mock analysis"
        
        # Если в тексте есть ключевые слова из категорий, считаем релевантным
        categories = filters_config.get("categories", [])
        
        for cat in categories:
            if cat.lower() in text_lower:
                is_relevant = True
                category = cat
                confidence = 0.8 + (random.random() * 0.15) # 0.80 - 0.95
                reason = f"Found keyword: {cat}"
                break
        
        # Если не нашли по категориям, проверяем на 'python' или 'tech' как fallback для теста
        if not is_relevant and ("python" in text_lower or "технологии" in text_lower):
            is_relevant = True
            category = categories[0] if categories else "Tech"
            confidence = 0.75
            reason = "Found general tech keywords"
            
        return {
            "is_relevant": is_relevant,
            "category": category,
            "confidence": round(confidence, 2),
            "reason": reason
        }

    async def health_check(self) -> bool:
        """Проверка доступности сервиса"""
        return True
