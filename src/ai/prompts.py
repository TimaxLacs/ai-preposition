from typing import List, Optional
import json

class PromptTemplate:
    """Шаблоны промптов для AI"""
    
    # Базовый системный промпт
    SYSTEM_PROMPT = """
    Ты эксперт по анализу и классификации контента из социальных сетей.
    Твоя задача - определить, соответствует ли пост заданным критериям и к какой категории он относится.
    Всегда отвечай в строгом формате JSON.
    """

    @staticmethod
    def format_analysis_prompt(text: str, categories: List[str], custom_prompt: Optional[str] = None) -> str:
        """
        Формирует промпт для анализа поста
        """
        base_prompt = custom_prompt or "Проанализируй этот пост."
        
        categories_str = ", ".join(categories)
        
        return f"""
        {base_prompt}
        
        Текст поста:
        \"\"\"{text}\"\"\"
        
        Доступные категории: {categories_str}
        
        Проанализируй текст и верни ответ в формате JSON:
        {{
            "is_relevant": true/false (подходит ли под критерии),
            "category": "название категории из списка или 'Other'",
            "confidence": 0.0-1.0 (твоя уверенность),
            "reason": "краткое объяснение решения"
        }}
        """





