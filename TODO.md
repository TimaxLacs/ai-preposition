# TODO: Полная реализация AI Post Filter

Подробный план реализации проекта со всем функционалом.

**Технологии:**
- Python 3.11+
- PostgreSQL (БД)
- Redis (кэш)
- Telethon (Telegram)
- vk_api (VK)
- FastAPI (REST API)
- AI API (провайдер выбирается позже)
- SQLAlchemy + Alembic (ORM и миграции)

---

## Фаза 1: Настройка инфраструктуры

### 1.1 Окружение и зависимости
- [ ] Обновить requirements.txt с PostgreSQL зависимостями
  - [ ] Добавить `psycopg2-binary` или `asyncpg`
  - [ ] Добавить `redis`
  - [ ] Добавить `celery` (для очередей)
- [ ] Создать `pyproject.toml` для Poetry (опционально)
- [ ] Настроить `.env` с PostgreSQL параметрами
- [ ] Создать `docker-compose.yml` для локальной разработки (PostgreSQL + Redis)

### 1.2 База данных PostgreSQL
- [ ] Установить PostgreSQL локально или через Docker
- [ ] Создать базу данных `ai_preposition`
- [ ] Настроить `src/storage/database.py` с SQLAlchemy engine
- [ ] Настроить Alembic для миграций
  - [ ] `alembic init migrations`
  - [ ] Настроить `alembic.ini`
  - [ ] Создать `env.py` для автогенерации миграций

### 1.3 Модели БД
- [ ] Создать `src/storage/models.py` с ORM моделями:
  - [ ] Таблица `filters` (id, name, prompt, categories, threshold, created_at)
  - [ ] Таблица `sources` (id, type, source_id, enabled, created_at)
  - [ ] Таблица `source_filters` (source_id, filter_id) - связь many-to-many
  - [ ] Таблица `processed_posts` (id, source_type, source_id, post_id, text, filter_result, was_forwarded, processed_at)
  - [ ] Индексы для быстрого поиска
- [ ] Создать первую миграцию: `alembic revision --autogenerate -m "Initial schema"`
- [ ] Применить миграцию: `alembic upgrade head`

### 1.4 Redis для кэша
- [ ] Установить Redis локально или через Docker
- [ ] Создать `src/storage/cache.py` с Redis клиентом
- [ ] Реализовать функции:
  - [ ] `cache_post_result(post_hash, result, ttl)`
  - [ ] `get_cached_result(post_hash)`
  - [ ] `is_post_processed(post_id)`
  - [ ] `mark_post_processed(post_id)`

---

## Фаза 2: AI модуль

### 2.1 Базовый AI клиент
- [ ] Реализовать `src/ai/client.py` (сейчас заглушка)
  - [ ] Выбрать AI провайдер (Groq/HuggingFace/Together/OpenRouter)
  - [ ] Реализовать `analyze_post()` с реальным API
  - [ ] Добавить обработку ошибок и retry логику
  - [ ] Добавить rate limiting (не больше N запросов/минуту)
  - [ ] Реализовать `health_check()`

### 2.2 Система промптов
- [ ] Создать `src/ai/prompts.py` с шаблонами промптов
  - [ ] Класс `PromptTemplate` для форматирования
  - [ ] Базовые промпты для фильтрации
  - [ ] Промпты для категоризации
  - [ ] Few-shot примеры в промптах
- [ ] Создать `src/ai/parsers.py` для парсинга ответов
  - [ ] Парсинг JSON ответов
  - [ ] Валидация структуры ответа
  - [ ] Обработка некорректных ответов

### 2.3 Тестирование AI
- [ ] Создать `tests/test_ai.py`
  - [ ] Тест подключения к AI API
  - [ ] Тест анализа тестового поста
  - [ ] Тест обработки ошибок
  - [ ] Тест rate limiting

---

## Фаза 3: Telegram провайдер

### 3.1 Базовый клиент
- [ ] Создать `src/providers/telegram/client.py`
  - [ ] Класс `TelegramProvider` с инициализацией Telethon
  - [ ] Метод `start()` - авторизация
  - [ ] Метод `stop()` - graceful shutdown
  - [ ] Обработка сессии и переподключений

### 3.2 Чтение постов
- [ ] Реализовать `get_channel_history(channel, limit)` - получение истории
- [ ] Реализовать `listen_new_messages(channels)` - мониторинг новых постов
- [ ] Обработка разных типов сообщений:
  - [ ] Текстовые посты
  - [ ] Посты с медиа (фото, видео)
  - [ ] Пересланные сообщения
  - [ ] Форматирование (entities)

### 3.3 Отправка результатов
- [ ] Реализовать `forward_message(message, to_channel)` - пересылка
- [ ] Реализовать `send_message(channel, text)` - отправка комментария
- [ ] Форматирование результатов (категория, уверенность, причина)
- [ ] Обработка ошибок отправки

### 3.4 Тестирование
- [ ] Создать `tests/test_telegram.py`
  - [ ] Mock тесты для основных методов
  - [ ] Тест чтения канала
  - [ ] Тест обработки разных типов сообщений

---

## Фаза 4: VK провайдер

### 4.1 Базовый клиент
- [ ] Создать `src/providers/vk/client.py`
  - [ ] Класс `VKProvider` с инициализацией vk_api
  - [ ] Метод `start()` - инициализация сессии
  - [ ] Метод `stop()` - завершение

### 4.2 Чтение постов
- [ ] Реализовать `get_wall_posts(group_id, count)` - получение постов
- [ ] Реализовать `listen_new_posts(groups)` - Long Polling для новых постов
- [ ] Обработка вложений:
  - [ ] Фото
  - [ ] Видео
  - [ ] Документы
  - [ ] Репосты

### 4.3 Отправка результатов
- [ ] Реализовать `post_to_wall(group_id, text)` - публикация
- [ ] Реализовать `send_message(user_id, text)` - личные сообщения
- [ ] Форматирование результатов для VK

### 4.4 Тестирование
- [ ] Создать `tests/test_vk.py`
  - [ ] Mock тесты
  - [ ] Тест чтения группы
  - [ ] Тест обработки вложений

---

## Фаза 5: Система фильтров

### 5.1 Модели и хранилище
- [ ] Создать `src/filters/models.py` с Pydantic моделями
  - [ ] `Filter` - модель фильтра
  - [ ] `SourceConfig` - модель источника
  - [ ] `FilterResult` - результат применения фильтра
- [ ] Создать `src/storage/repositories/filters.py`
  - [ ] CRUD операции для фильтров
  - [ ] `create_filter(filter_data)`
  - [ ] `get_filter(filter_id)`
  - [ ] `update_filter(filter_id, data)`
  - [ ] `delete_filter(filter_id)`
  - [ ] `list_filters()`
- [ ] Создать `src/storage/repositories/sources.py`
  - [ ] CRUD для источников
  - [ ] Связь источников с фильтрами

### 5.2 Движок фильтров
- [ ] Создать `src/filters/engine.py`
  - [ ] Класс `FilterEngine(ai_client)`
  - [ ] Метод `apply_filters(post, filters)` - применение фильтров
  - [ ] Метод `should_forward(filter_result, threshold)` - решение о пересылке
  - [ ] Комбинирование результатов нескольких фильтров
  - [ ] Логирование решений

### 5.3 Загрузка из YAML
- [ ] Создать `src/config/loader.py`
  - [ ] Функция `load_filters_config()` - загрузка из `config/filters.yaml`
  - [ ] Функция `load_sources_config()` - загрузка из `config/sources.yaml`
  - [ ] Валидация конфигов
  - [ ] Синхронизация с БД (создание/обновление)

### 5.4 Тестирование
- [ ] Создать `tests/test_filters.py`
  - [ ] Тест применения фильтра
  - [ ] Тест комбинирования фильтров
  - [ ] Тест загрузки из YAML

---

## Фаза 6: Основная бизнес-логика

### 6.1 Обработчик постов
- [ ] Создать `src/core/processor.py`
  - [ ] Класс `PostProcessor(ai_client, filter_engine, db, cache)`
  - [ ] Метод `process_post(post, source_config)` - полная обработка поста:
    - [ ] Проверка в кэше (уже обработан?)
    - [ ] Извлечение текста
    - [ ] Применение фильтров через AI
    - [ ] Сохранение результата в БД
    - [ ] Кэширование
    - [ ] Возврат решения (forward/skip)

### 6.2 Дедупликация
- [ ] Создать `src/core/deduplicator.py`
  - [ ] Функция `get_post_hash(text)` - хеш текста
  - [ ] Функция `is_duplicate(post_hash, db, cache)` - проверка дубликата
  - [ ] Функция `mark_as_processed(post_hash, cache)`

### 6.3 Пересылка постов
- [ ] Создать `src/core/forwarder.py`
  - [ ] Класс `Forwarder(telegram_client, vk_client)`
  - [ ] Метод `forward_to_telegram(message, channel, category, confidence)`
  - [ ] Метод `forward_to_vk(post, group_id, category, confidence)`
  - [ ] Форматирование сообщений с результатами

### 6.4 Главный координатор
- [ ] Создать `src/core/coordinator.py`
  - [ ] Класс `Coordinator` - управляет всем процессом
  - [ ] Метод `start()` - запуск всех провайдеров
  - [ ] Метод `stop()` - graceful shutdown
  - [ ] Регистрация обработчиков для новых постов
  - [ ] Обработка ошибок и перезапуск

### 6.5 Тестирование
- [ ] Создать `tests/test_processor.py`
- [ ] Создать `tests/test_coordinator.py`
- [ ] Интеграционные тесты полного flow

---

## Фаза 7: REST API

### 7.1 Базовое приложение
- [ ] Создать `src/api/main.py`
  - [ ] Инициализация FastAPI приложения
  - [ ] Middleware (CORS, логирование)
  - [ ] Обработка ошибок
  - [ ] Healthcheck endpoint

### 7.2 Аутентификация
- [ ] Создать `src/api/auth.py`
  - [ ] Bearer token аутентификация
  - [ ] Dependency для защищенных endpoints
  - [ ] Хранение токенов в .env

### 7.3 Endpoints для фильтров
- [ ] Создать `src/api/routes/filters.py`
  - [ ] `POST /api/v1/filters` - создать фильтр
  - [ ] `GET /api/v1/filters` - список фильтров
  - [ ] `GET /api/v1/filters/{id}` - получить фильтр
  - [ ] `PUT /api/v1/filters/{id}` - обновить фильтр
  - [ ] `DELETE /api/v1/filters/{id}` - удалить фильтр
  - [ ] `POST /api/v1/filters/test` - протестировать фильтр на тексте

### 7.4 Endpoints для источников
- [ ] Создать `src/api/routes/sources.py`
  - [ ] `POST /api/v1/sources` - добавить источник
  - [ ] `GET /api/v1/sources` - список источников
  - [ ] `GET /api/v1/sources/{id}` - получить источник
  - [ ] `PUT /api/v1/sources/{id}` - обновить источник
  - [ ] `DELETE /api/v1/sources/{id}` - удалить источник
  - [ ] `POST /api/v1/sources/{id}/enable` - включить
  - [ ] `POST /api/v1/sources/{id}/disable` - отключить

### 7.5 Endpoints для статистики
- [ ] Создать `src/api/routes/stats.py`
  - [ ] `GET /api/v1/stats` - общая статистика
  - [ ] `GET /api/v1/stats/filters/{id}` - статистика по фильтру
  - [ ] `GET /api/v1/stats/sources/{id}` - статистика по источнику
  - [ ] `GET /api/v1/posts` - список обработанных постов (с пагинацией)
  - [ ] `GET /api/v1/posts/{id}` - детали поста

### 7.6 Pydantic модели
- [ ] Создать `src/api/schemas.py`
  - [ ] Request/Response модели для всех endpoints
  - [ ] Валидация входных данных

### 7.7 Тестирование API
- [ ] Создать `tests/test_api/`
  - [ ] Тесты для каждого endpoint
  - [ ] Тест аутентификации
  - [ ] Тест валидации

---

## Фаза 8: Настройки и конфигурация

### 8.1 Система настроек
- [ ] Создать `src/config/settings.py`
  - [ ] Класс `Settings` на базе Pydantic Settings
  - [ ] Загрузка из .env
  - [ ] Валидация всех настроек
  - [ ] Singleton паттерн для настроек

### 8.2 Логирование
- [ ] Создать `src/utils/logger.py`
  - [ ] Настройка Loguru
  - [ ] Разные уровни логирования
  - [ ] Ротация логов
  - [ ] Форматирование

### 8.3 Утилиты
- [ ] Создать `src/utils/helpers.py`
  - [ ] Функции для работы с текстом
  - [ ] Хеширование
  - [ ] Валидация URL/ID
  - [ ] Форматирование дат

---

## Фаза 9: Очереди и фоновые задачи

### 9.1 Celery для асинхронной обработки
- [ ] Создать `src/tasks/celery_app.py`
  - [ ] Инициализация Celery с Redis broker
  - [ ] Базовая конфигурация

### 9.2 Задачи
- [ ] Создать `src/tasks/posts.py`
  - [ ] Task `process_post_async(post_data)` - асинхронная обработка
  - [ ] Task `cleanup_old_posts()` - очистка старых записей
  - [ ] Task `update_stats()` - обновление статистики

### 9.3 Периодические задачи
- [ ] Настроить Celery Beat для периодических задач
  - [ ] Очистка кэша каждые 24 часа
  - [ ] Очистка старых постов из БД (>30 дней)
  - [ ] Обновление статистики каждый час

---

## Фаза 10: Деплой и продакшен

### 10.1 Docker
- [ ] Создать `Dockerfile` для приложения
  - [ ] Multi-stage build для оптимизации
  - [ ] Production образ
- [ ] Обновить `docker-compose.yml` для продакшена
  - [ ] PostgreSQL
  - [ ] Redis
  - [ ] Application
  - [ ] Nginx (reverse proxy)
  - [ ] Celery worker
  - [ ] Celery beat

### 10.2 Миграции и инициализация
- [ ] Создать `scripts/init_db.py` - инициализация БД
- [ ] Создать `scripts/seed_data.py` - тестовые данные
- [ ] Создать `scripts/migrate.sh` - запуск миграций

### 10.3 Systemd service (для VPS без Docker)
- [ ] Создать `deployment/ai-filter.service`
- [ ] Создать `deployment/celery-worker.service`
- [ ] Создать `deployment/celery-beat.service`
- [ ] Инструкции по установке

### 10.4 Nginx конфигурация
- [ ] Создать `deployment/nginx.conf`
  - [ ] Reverse proxy для API
  - [ ] SSL настройки
  - [ ] Rate limiting

### 10.5 Мониторинг
- [ ] Настроить healthchecks для всех компонентов
- [ ] Настроить алерты в Telegram при ошибках
- [ ] Логирование в файлы с ротацией

### 10.6 Бэкапы
- [ ] Скрипт `scripts/backup_db.sh` - бэкап PostgreSQL
- [ ] Настроить cron для автоматических бэкапов
- [ ] Хранение бэкапов (локально или S3)

---

## Фаза 11: Тестирование и качество

### 11.1 Unit тесты
- [ ] Покрытие тестами >80%
- [ ] Тесты для всех модулей
- [ ] Mock внешних зависимостей

### 11.2 Integration тесты
- [ ] Тесты с реальной БД (test database)
- [ ] Тесты провайдеров (с моками API)
- [ ] Тесты полного flow

### 11.3 E2E тесты
- [ ] Тест полного сценария: пост → анализ → пересылка
- [ ] Тест обработки ошибок

### 11.4 Линтинг и форматирование
- [ ] Настроить ruff для линтинга
- [ ] Настроить black для форматирования
- [ ] Настроить mypy для проверки типов
- [ ] pre-commit hooks для автопроверки

---

## Фаза 12: Документация

### 12.1 Код
- [ ] Docstrings для всех классов и функций
- [ ] Type hints везде
- [ ] Комментарии в сложных местах

### 12.2 API документация
- [ ] Swagger UI (автоматически через FastAPI)
- [ ] Примеры запросов для всех endpoints
- [ ] Описание моделей данных

### 12.3 Документация для пользователей
- [ ] Обновить README.md с финальной версией
- [ ] Инструкция по установке
- [ ] Инструкция по конфигурации
- [ ] FAQ
- [ ] Troubleshooting guide

### 12.4 Документация для разработчиков
- [ ] Архитектура проекта
- [ ] Описание модулей
- [ ] Как добавить новый провайдер
- [ ] Как добавить новый AI backend
- [ ] Contributing guide

---

## Дополнительные задачи (опционально)

### Web UI (если нужен)
- [ ] Создать фронтенд (React/Vue)
- [ ] Дашборд со статистикой
- [ ] Управление фильтрами через UI
- [ ] Управление источниками
- [ ] Просмотр обработанных постов
- [ ] Real-time обновления (WebSocket)

### Расширенная аналитика
- [ ] Графики активности постов
- [ ] Тренды по категориям
- [ ] Популярные темы
- [ ] Экспорт данных (CSV, JSON)

### Дополнительные провайдеры
- [ ] Twitter/X интеграция
- [ ] Reddit интеграция
- [ ] RSS фиды

### Продвинутые фичи
- [ ] Semantic similarity для дедупликации (embeddings)
- [ ] Мультиязычность
- [ ] Пользовательские фильтры (если несколько пользователей)
- [ ] A/B тестирование фильтров

---

## Порядок реализации (рекомендуемый)

1. **Неделя 1-2:** Фазы 1-2 (Инфраструктура + AI)
2. **Неделя 3-4:** Фаза 3 (Telegram)
3. **Неделя 5:** Фаза 4 (VK)
4. **Неделя 6-7:** Фазы 5-6 (Фильтры + Бизнес-логика)
5. **Неделя 8-9:** Фаза 7 (REST API)
6. **Неделя 10:** Фаза 8 (Настройки)
7. **Неделя 11:** Фаза 9 (Очереди)
8. **Неделя 12:** Фаза 10 (Деплой)
9. **Неделя 13:** Фазы 11-12 (Тесты + Документация)

**Итого: ~3 месяца** (работая 15-20 часов/неделю)

---

## Критерии завершения

### MVP готов когда:
- [ ] Работает обработка постов из Telegram
- [ ] AI анализирует посты
- [ ] Результаты сохраняются в PostgreSQL
- [ ] Подходящие посты пересылаются в выходной канал

### v1.0 готова когда:
- [ ] Все фазы 1-10 завершены
- [ ] Работает Telegram + VK
- [ ] REST API функционирует
- [ ] Есть базовые тесты
- [ ] Задеплоено на сервере
- [ ] Работает стабильно 24/7

### Production-ready когда:
- [ ] Покрытие тестами >80%
- [ ] Мониторинг настроен
- [ ] Автоматические бэкапы
- [ ] Документация полная
- [ ] Обработка ошибок везде
- [ ] Rate limiting настроен
- [ ] Security audit пройден

