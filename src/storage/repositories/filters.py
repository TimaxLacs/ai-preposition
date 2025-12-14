from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models import Filter

class FilterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, filter_data: dict) -> Filter:
        new_filter = Filter(**filter_data)
        self.session.add(new_filter)
        await self.session.commit()
        await self.session.refresh(new_filter)
        return new_filter

    async def get_by_id(self, filter_id: str) -> Optional[Filter]:
        query = select(Filter).where(Filter.id == filter_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Filter]:
        query = select(Filter).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, filter_id: str, update_data: dict) -> Optional[Filter]:
        query = update(Filter).where(Filter.id == filter_id).values(**update_data).returning(Filter)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, filter_id: str) -> bool:
        query = delete(Filter).where(Filter.id == filter_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0





