import logging
from typing import List, Dict, Optional, Any
from ..ai.client import AIClient
from ..ai.prompts import PromptTemplate
from ..storage.models import Filter

logger = logging.getLogger(__name__)

class FilterResult:
    def __init__(self, is_relevant: bool, category: str, confidence: float, reason: str, filter_id: str):
        self.is_relevant = is_relevant
        self.category = category
        self.confidence = confidence
        self.reason = reason
        self.filter_id = filter_id
        
    def to_dict(self):
        return {
            "is_relevant": self.is_relevant,
            "category": self.category,
            "confidence": self.confidence,
            "reason": self.reason,
            "filter_id": self.filter_id
        }

class FilterEngine:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def apply_filters(self, text: str, filters: List[Filter]) -> Optional[FilterResult]:
        """
        Применяет список фильтров к тексту.
        Возвращает первый положительный результат или лучший результат.
        """
        best_result = None
        
        for filter_model in filters:
            if not filter_model.enabled:
                continue

            try:
                # Формируем конфигурацию для AI
                filters_config = {
                    "categories": filter_model.categories,
                    "prompt": filter_model.prompt
                }
                
                # Запрашиваем AI
                # TODO: Оптимизация - объединять фильтры в один запрос если возможно
                ai_response = await self.ai_client.analyze_post(text, filters_config)
                
                result = FilterResult(
                    is_relevant=ai_response["is_relevant"],
                    category=ai_response["category"],
                    confidence=ai_response["confidence"],
                    reason=ai_response["reason"],
                    filter_id=filter_model.id
                )
                
                logger.info(f"Filter '{filter_model.name}' result: {result.to_dict()}")
                
                # Проверяем порог уверенности
                if result.is_relevant and result.confidence >= filter_model.threshold:
                    # Если нашли подходящий - сразу возвращаем (First Match стратегия)
                    # Можно изменить на поиск лучшего (Best Match)
                    return result
                    
            except Exception as e:
                logger.error(f"Error applying filter {filter_model.id}: {e}")
                
        return None





