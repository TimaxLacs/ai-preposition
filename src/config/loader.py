import yaml
import os
import logging
from typing import Dict, Any
from ..storage.database import async_session_maker
from ..storage.repositories.filters import FilterRepository
from ..storage.repositories.sources import SourceRepository

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, filename)
        if not os.path.exists(path):
            logger.warning(f"Config file {path} not found")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    async def sync_filters(self):
        """Синхронизация фильтров из YAML в БД"""
        data = self.load_yaml("filters.yaml")
        if not data or "filters" not in data:
            return

        async with async_session_maker() as session:
            repo = FilterRepository(session)
            
            for filter_data in data["filters"]:
                existing = await repo.get_by_id(filter_data["id"])
                
                filter_obj = {
                    "id": filter_data["id"],
                    "name": filter_data["name"],
                    "prompt": filter_data["prompt"],
                    "categories": filter_data["categories"],
                    "threshold": filter_data.get("threshold", 0.7),
                    "enabled": filter_data.get("enabled", True)
                }
                
                if existing:
                    await repo.update(filter_data["id"], filter_obj)
                    logger.info(f"Updated filter: {filter_data['id']}")
                else:
                    await repo.create(filter_obj)
                    logger.info(f"Created filter: {filter_data['id']}")

    async def sync_sources(self):
        """Синхронизация источников из YAML в БД"""
        data = self.load_yaml("sources.yaml")
        if not data:
            return

        async with async_session_maker() as session:
            repo = SourceRepository(session)
            
            # Telegram
            if "telegram" in data:
                for src in data["telegram"]:
                    await self._sync_source(repo, "telegram", src)
            
            # VK
            if "vk" in data:
                for src in data["vk"]:
                    # VK конфиг может использовать 'group' вместо 'channel'
                    src["channel"] = src.get("group") or src.get("channel")
                    await self._sync_source(repo, "vk", src)

    async def _sync_source(self, repo: SourceRepository, type_: str, data: dict):
        source_id = data.get("channel")
        if not source_id:
            return
            
        source_obj = {
            "type": type_,
            "source_id": source_id,
            "name": data.get("name"),
            "enabled": data.get("enabled", True),
            "check_interval": data.get("check_interval", 60),
            "filter_ids": data.get("filters", [])
        }
        
        existing = await repo.get_by_source_id(source_id)
        if not existing:
            await repo.create(source_obj)
            logger.info(f"Created source: {source_id}")
        else:
            # Обновляем фильтры
            if "filters" in data:
                await repo.update_filters(existing.id, data["filters"])
                logger.info(f"Updated source filters: {source_id}")





