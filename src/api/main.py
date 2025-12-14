import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..storage.cache import cache
from .routes import filters, sources
from ..core.coordinator import Coordinator
from ..config.loader import ConfigLoader

logger = logging.getLogger(__name__)

# Глобальная переменная для координатора
coordinator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting...")
    
    # 1. Подключение к кэшу
    await cache.connect()
    
    # 2. Загрузка конфигурации
    config_loader = ConfigLoader()
    try:
        await config_loader.sync_filters()
        await config_loader.sync_sources()
    except Exception as e:
        logger.error(f"Failed to sync config: {e}")

    # 3. Запуск координатора (в фоне)
    global coordinator
    coordinator = Coordinator()
    
    # Запускаем координатор как фоновую задачу
    coordinator_task = asyncio.create_task(coordinator.start())
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    if coordinator:
        await coordinator.stop()
        try:
            await coordinator_task
        except asyncio.CancelledError:
            pass
            
    await cache.close()

app = FastAPI(
    title="AI Post Filter API",
    description="API for managing filters and sources for AI Post Filter system",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роуты
app.include_router(filters.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "coordinator": "running" if coordinator and coordinator.is_running else "stopped"}
