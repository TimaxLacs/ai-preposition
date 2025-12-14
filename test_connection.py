#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к сервисам
Используйте его чтобы проверить правильность настройки перед запуском бота

Запуск: python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

print("="*60)
print("🧪 Тестирование подключения к сервисам")
print("="*60)
print()

# ===== ПРОВЕРКА .ENV =====
print("📋 Шаг 1: Проверка .env файла")
print("-"*60)

required_vars = {
    'GROQ_API_KEY': 'Groq API ключ',
    'TELEGRAM_API_ID': 'Telegram API ID',
    'TELEGRAM_API_HASH': 'Telegram API Hash',
    'TELEGRAM_PHONE': 'Telegram номер телефона',
    'TELEGRAM_OUTPUT_CHANNEL': 'Telegram выходной канал',
}

missing_vars = []
for var, description in required_vars.items():
    value = os.getenv(var)
    if not value or value.startswith('your_') or value == '12345678':
        print(f"❌ {description} ({var}): НЕ НАСТРОЕН")
        missing_vars.append(var)
    else:
        # Скрыть часть значения для безопасности
        if 'KEY' in var or 'HASH' in var or 'TOKEN' in var:
            display_value = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
        else:
            display_value = value
        print(f"✅ {description} ({var}): {display_value}")

print()

if missing_vars:
    print("⚠️  ВНИМАНИЕ: Не все переменные настроены!")
    print(f"   Настройте: {', '.join(missing_vars)}")
    print(f"   Отредактируйте файл .env")
    print()
    response = input("Продолжить тестирование? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)
else:
    print("✅ Все переменные окружения настроены!")

print()

# ===== ТЕСТ GROQ API =====
print("🤖 Шаг 2: Тестирование Groq API")
print("-"*60)

try:
    from groq import Groq
    
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key or groq_key.startswith('your_'):
        print("⚠️  Groq API ключ не настроен, пропускаем тест")
    else:
        print("   Создание клиента...")
        client = Groq(api_key=groq_key)
        
        print("   Отправка тестового запроса...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Скажи привет на русском (одно слово)"}
            ],
            max_tokens=10,
            temperature=0.5
        )
        
        result = response.choices[0].message.content
        print(f"   Ответ от AI: {result}")
        print("✅ Groq API работает!")
        
except ImportError:
    print("❌ Библиотека groq не установлена")
    print("   Установите: pip install groq")
except Exception as e:
    print(f"❌ Ошибка при тестировании Groq API: {e}")
    print("   Проверьте правильность API ключа")

print()

# ===== ТЕСТ TELEGRAM =====
print("📱 Шаг 3: Тестирование Telegram API")
print("-"*60)

try:
    from telethon import TelegramClient
    import asyncio
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    output_channel = os.getenv('TELEGRAM_OUTPUT_CHANNEL')
    
    if not all([api_id, api_hash, phone]) or api_id == '12345678':
        print("⚠️  Telegram credentials не настроены, пропускаем тест")
    else:
        async def test_telegram():
            print("   Создание клиента...")
            client = TelegramClient('test_session', int(api_id), api_hash)
            
            try:
                print("   Подключение к Telegram...")
                print("   (При первом запуске попросит код из SMS)")
                await client.start(phone=phone)
                
                print("✅ Успешно подключено к Telegram!")
                
                # Проверка доступа к себе
                me = await client.get_me()
                print(f"   Аккаунт: {me.first_name} (@{me.username or 'no username'})")
                
                # Проверка выходного канала
                if output_channel and not output_channel.startswith('@your_'):
                    print(f"   Проверка доступа к каналу {output_channel}...")
                    try:
                        entity = await client.get_entity(output_channel)
                        print(f"✅ Доступ к каналу подтвержден: {entity.title}")
                    except Exception as e:
                        print(f"❌ Не удалось получить доступ к каналу: {e}")
                        print("   Убедитесь что:")
                        print("   - Канал существует")
                        print("   - Вы подписаны на канал")
                        print("   - Правильно указан username (@channel)")
                
                print("✅ Telegram API работает!")
                
            except Exception as e:
                print(f"❌ Ошибка подключения к Telegram: {e}")
            finally:
                await client.disconnect()
        
        asyncio.run(test_telegram())
        
except ImportError:
    print("❌ Библиотека telethon не установлена")
    print("   Установите: pip install telethon")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")

print()

# ===== ТЕСТ VK (опционально) =====
print("🔵 Шаг 4: Тестирование VK API (опционально)")
print("-"*60)

vk_token = os.getenv('VK_TOKEN')
if not vk_token or vk_token.startswith('your_') or vk_token.startswith('vk1.a.your'):
    print("⚠️  VK токен не настроен, пропускаем тест")
else:
    try:
        import vk_api
        
        print("   Создание сессии...")
        vk_session = vk_api.VkApi(token=vk_token)
        vk = vk_session.get_api()
        
        print("   Получение информации о пользователе...")
        user = vk.users.get()[0]
        print(f"   Аккаунт: {user['first_name']} {user['last_name']}")
        print("✅ VK API работает!")
        
    except ImportError:
        print("⚠️  Библиотека vk_api не установлена")
        print("   Установите: pip install vk-api")
    except Exception as e:
        print(f"❌ Ошибка при тестировании VK API: {e}")
        print("   Проверьте правильность токена")

print()

# ===== ПРОВЕРКА ЗАВИСИМОСТЕЙ =====
print("📦 Шаг 5: Проверка установленных пакетов")
print("-"*60)

required_packages = {
    'groq': 'Groq API клиент',
    'telethon': 'Telegram клиент',
    'python-dotenv': 'Загрузка .env файлов',
    'loguru': 'Логирование',
}

optional_packages = {
    'vk_api': 'VK API клиент',
    'fastapi': 'REST API фреймворк',
    'sqlalchemy': 'ORM для БД',
}

for package, description in required_packages.items():
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {description} ({package})")
    except ImportError:
        print(f"❌ {description} ({package}) - НЕ УСТАНОВЛЕН")

print()
print("Опциональные пакеты:")
for package, description in optional_packages.items():
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {description} ({package})")
    except ImportError:
        print(f"⚠️  {description} ({package}) - не установлен")

print()

# ===== ПРОВЕРКА ФАЙЛОВ =====
print("📁 Шаг 6: Проверка структуры проекта")
print("-"*60)

required_files = [
    'main_mvp.py',
    'requirements.txt',
    '.env.example',
    '.gitignore',
]

for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - НЕ НАЙДЕН")

# Проверка папок
if not os.path.exists('logs'):
    print("⚠️  Папка logs/ не существует")
    print("   Создайте: mkdir logs")
else:
    print("✅ logs/")

print()

# ===== ИТОГ =====
print("="*60)
print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ")
print("="*60)

if missing_vars:
    print("❌ Настройка не завершена")
    print(f"   Необходимо настроить: {', '.join(missing_vars)}")
    print()
    print("📝 Следующие шаги:")
    print("   1. Отредактируйте .env файл")
    print("   2. Заполните все обязательные поля")
    print("   3. Запустите этот скрипт снова")
else:
    print("✅ Всё готово к запуску!")
    print()
    print("🚀 Следующие шаги:")
    print("   1. Запустите MVP: python main_mvp.py")
    print("   2. При первом запуске введите код из Telegram")
    print("   3. Дождитесь новых постов в каналах")
    print()
    print("📚 Документация:")
    print("   • QUICKSTART.md - подробная инструкция")
    print("   • IMPLEMENTATION_PLAN.md - план развития проекта")

print("="*60)
