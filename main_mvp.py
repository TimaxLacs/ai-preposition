#!/usr/bin/env python3
"""
AI Post Filter - MVP версия
Минимальная рабочая версия для быстрого тестирования

Установка:
    pip install telethon groq python-dotenv loguru

Настройка:
    1. Скопировать .env.example в .env
    2. Заполнить все ключи API
    3. Указать каналы для мониторинга
    4. Запустить: python main_mvp.py

При первом запуске Telegram попросит код из SMS.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional

from dotenv import load_dotenv
from loguru import logger
from telethon import TelegramClient, events

try:
    from groq import Groq
except ImportError:
    logger.error("Groq не установлен. Установите: pip install groq")
    sys.exit(1)

# Загрузка переменных окружения
load_dotenv()

# ===== КОНФИГУРАЦИЯ =====

# AI API
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY не найден в .env файле!")
    sys.exit(1)

# Telegram
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_OUTPUT_CHANNEL = os.getenv('TELEGRAM_OUTPUT_CHANNEL', '@your_output_channel')

if not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]):
    logger.error("Telegram credentials не найдены в .env файле!")
    sys.exit(1)

try:
    TELEGRAM_API_ID = int(TELEGRAM_API_ID)
except ValueError:
    logger.error("TELEGRAM_API_ID должен быть числом!")
    sys.exit(1)

# Каналы для мониторинга (можно изменить)
SOURCE_CHANNELS = [
    '@tproger',
    '@python_digest',
    # Добавьте свои каналы здесь
]

# Настройки фильтрации
CONFIDENCE_THRESHOLD = float(os.getenv('DEFAULT_CONFIDENCE_THRESHOLD', '0.7'))

# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/mvp_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)

# ===== AI КЛИЕНТ =====

groq_client = Groq(api_key=GROQ_API_KEY)


def analyze_post_with_ai(text: str) -> Optional[Dict]:
    """
    Анализирует пост с помощью AI
    
    Args:
        text: Текст поста
        
    Returns:
        Dict с результатами анализа или None при ошибке
    """
    prompt = f"""
Проанализируй следующий пост и определи:
1. Относится ли он к технологиям, программированию или IT?
2. Если да, к какой категории?
3. Насколько ты уверен в своем ответе?

Пост: {text}

Категории:
- AI/ML: Искусственный интеллект, машинное обучение
- Web Development: Веб-разработка, фреймворки
- DevOps: CI/CD, контейнеризация, облачные технологии
- Security: Информационная безопасность
- Mobile: Разработка мобильных приложений
- Job: Вакансии и предложения работы
- Education: Обучающий контент, туториалы
- Other: Другие технологические темы

Ответь строго в формате JSON:
{{
    "is_relevant": true или false,
    "category": "название категории из списка",
    "confidence": число от 0.0 до 1.0,
    "reason": "краткое объяснение (1-2 предложения на русском)"
}}
"""
    
    try:
        logger.debug("Отправка запроса к AI...")
        
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Ты - эксперт по анализу технологического контента. "
                              "Отвечай только в формате JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        logger.debug(f"AI ответ: {result}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON от AI: {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при обращении к AI: {e}")
        return None


# ===== СТАТИСТИКА =====

class Statistics:
    """Простая статистика работы бота"""
    
    def __init__(self):
        self.total_processed = 0
        self.accepted = 0
        self.rejected = 0
        self.errors = 0
        self.start_time = datetime.now()
        self.categories = {}
    
    def add_accepted(self, category: str):
        self.accepted += 1
        self.total_processed += 1
        self.categories[category] = self.categories.get(category, 0) + 1
    
    def add_rejected(self):
        self.rejected += 1
        self.total_processed += 1
    
    def add_error(self):
        self.errors += 1
        self.total_processed += 1
    
    def get_summary(self) -> str:
        runtime = datetime.now() - self.start_time
        return (
            f"\n{'='*50}\n"
            f"📊 Статистика работы:\n"
            f"{'='*50}\n"
            f"⏱️  Время работы: {runtime}\n"
            f"📝 Обработано постов: {self.total_processed}\n"
            f"✅ Принято: {self.accepted} ({self.accepted/max(self.total_processed,1)*100:.1f}%)\n"
            f"❌ Отклонено: {self.rejected} ({self.rejected/max(self.total_processed,1)*100:.1f}%)\n"
            f"⚠️  Ошибок: {self.errors}\n"
            f"\n📊 По категориям:\n" +
            "\n".join(f"   • {cat}: {count}" for cat, count in self.categories.items()) +
            f"\n{'='*50}\n"
        )


stats = Statistics()


# ===== ОСНОВНАЯ ЛОГИКА =====

async def process_message(message, client: TelegramClient):
    """
    Обработка одного сообщения
    
    Args:
        message: Объект сообщения Telethon
        client: Telegram клиент
    """
    # Получаем текст
    text = message.text or message.message
    
    if not text or len(text.strip()) < 10:
        logger.debug("Пропускаем пост без текста или слишком короткий")
        return
    
    # Получаем информацию о канале
    try:
        chat = await message.get_chat()
        source_name = getattr(chat, 'username', None) or getattr(chat, 'title', 'Unknown')
    except:
        source_name = "Unknown"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📨 Новый пост из @{source_name}")
    logger.info(f"📝 Текст (первые 150 символов): {text[:150]}...")
    
    # Анализ через AI
    logger.info("🤖 Анализирую через AI...")
    result = analyze_post_with_ai(text)
    
    if not result:
        logger.error("❌ Ошибка анализа AI")
        stats.add_error()
        return
    
    is_relevant = result.get('is_relevant', False)
    category = result.get('category', 'Unknown')
    confidence = result.get('confidence', 0.0)
    reason = result.get('reason', 'Нет объяснения')
    
    logger.info(f"🎯 Результат: relevant={is_relevant}, "
               f"category={category}, "
               f"confidence={confidence:.2f}")
    logger.info(f"💭 Причина: {reason}")
    
    # Проверяем порог уверенности
    if is_relevant and confidence >= CONFIDENCE_THRESHOLD:
        logger.success(f"✅ Пост ПРИНЯТ (уверенность {confidence:.0%} >= {CONFIDENCE_THRESHOLD:.0%})")
        stats.add_accepted(category)
        
        try:
            # Пересылаем сообщение в целевой канал
            await client.forward_messages(
                entity=TELEGRAM_OUTPUT_CHANNEL,
                messages=message
            )
            
            # Добавляем комментарий с результатами анализа
            comment = (
                f"📌 Категория: **{category}**\n"
                f"🔍 Уверенность: **{confidence:.0%}**\n"
                f"💭 {reason}\n"
                f"📍 Источник: @{source_name}"
            )
            
            await client.send_message(
                entity=TELEGRAM_OUTPUT_CHANNEL,
                message=comment
            )
            
            logger.success(f"📤 Переслано в {TELEGRAM_OUTPUT_CHANNEL}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при пересылке: {e}")
            stats.add_error()
    
    else:
        reason_text = (
            f"не релевантен" if not is_relevant 
            else f"низкая уверенность ({confidence:.0%} < {CONFIDENCE_THRESHOLD:.0%})"
        )
        logger.info(f"❌ Пост ОТКЛОНЁН: {reason_text}")
        stats.add_rejected()
    
    logger.info(f"{'='*60}\n")


async def main():
    """Основная функция"""
    
    logger.info("="*60)
    logger.info("🚀 AI Post Filter MVP - Запуск")
    logger.info("="*60)
    logger.info(f"📱 Telegram: {TELEGRAM_PHONE}")
    logger.info(f"📢 Выходной канал: {TELEGRAM_OUTPUT_CHANNEL}")
    logger.info(f"🎯 Порог уверенности: {CONFIDENCE_THRESHOLD:.0%}")
    logger.info(f"📡 Мониторим каналы:")
    for channel in SOURCE_CHANNELS:
        logger.info(f"   • {channel}")
    logger.info("="*60)
    logger.info("")
    
    # Создаем Telegram клиент
    client = TelegramClient('ai_filter_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        # Подключаемся
        logger.info("🔌 Подключение к Telegram...")
        await client.start(phone=TELEGRAM_PHONE)
        logger.success("✅ Подключено к Telegram!")
        
        # Проверяем доступ к выходному каналу
        try:
            await client.get_entity(TELEGRAM_OUTPUT_CHANNEL)
            logger.success(f"✅ Доступ к каналу {TELEGRAM_OUTPUT_CHANNEL} подтвержден")
        except Exception as e:
            logger.error(f"❌ Не удалось получить доступ к каналу {TELEGRAM_OUTPUT_CHANNEL}: {e}")
            logger.error("Убедитесь, что канал существует и вы в нём состоите!")
            return
        
        logger.info("")
        logger.info("👀 Начинаю мониторинг каналов...")
        logger.info("💡 Нажмите Ctrl+C для остановки")
        logger.info("")
        
        # Обработчик новых сообщений
        @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
        async def handler(event):
            try:
                await process_message(event.message, client)
            except Exception as e:
                logger.exception(f"Неожиданная ошибка при обработке сообщения: {e}")
                stats.add_error()
        
        # Держим бота запущенным
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("\n⏸️  Получен сигнал остановки...")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
    finally:
        logger.info(stats.get_summary())
        logger.info("👋 Завершение работы...")
        await client.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Программа остановлена пользователем")
