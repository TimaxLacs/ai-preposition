from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from ..models import Source, Filter

class SourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, source_data: dict) -> Source:
        # filter_ids извлекаем отдельно, если они есть
        filter_ids = source_data.pop('filter_ids', [])
        
        source = Source(**source_data)
        
        if filter_ids:
            filters_query = select(Filter).where(Filter.id.in_(filter_ids))
            result = await self.session.execute(filters_query)
            filters = result.scalars().all()
            source.filters = list(filters)
            
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source

    async def get_by_source_id(self, source_id: str) -> Optional[Source]:
        query = select(Source).where(Source.source_id == source_id).options(selectinload(Source.filters))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_enabled(self) -> List[Source]:
        """Возвращает все активные источники с загруженными фильтрами"""
        query = select(Source).where(Source.enabled == True).options(selectinload(Source.filters))
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def list_all(self) -> List[Source]:
        query = select(Source).options(selectinload(Source.filters))
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_filters(self, source_id: int, filter_ids: List[str]):
        """Обновляет список фильтров для источника"""
        source = await self.session.get(Source, source_id)
        if not source:
            return None
            
        filters_query = select(Filter).where(Filter.id.in_(filter_ids))
        result = await self.session.execute(filters_query)
        filters = result.scalars().all()
        
        source.filters = list(filters)
        await self.session.commit()
        return source





