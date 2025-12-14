from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...storage.database import get_db
from ...storage.repositories.sources import SourceRepository
from ..schemas import SourceCreate, SourceResponse, SourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])

@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(source_data: SourceCreate, db: AsyncSession = Depends(get_db)):
    repo = SourceRepository(db)
    # Проверяем не дубликат ли (по source_id)
    if await repo.get_by_source_id(source_data.source_id):
        raise HTTPException(status_code=400, detail="Source with this ID already exists")
    
    return await repo.create(source_data.model_dump())

@router.get("/", response_model=List[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    repo = SourceRepository(db)
    return await repo.list_all()

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(source_id: int, source_data: SourceUpdate, db: AsyncSession = Depends(get_db)):
    repo = SourceRepository(db)
    # Здесь упрощенная логика, в реальности нужно обрабатывать обновление фильтров отдельно или здесь же
    # Пока реализуем только обновление фильтров если они переданы
    if source_data.filter_ids is not None:
        updated = await repo.update_filters(source_id, source_data.filter_ids)
        if not updated:
            raise HTTPException(status_code=404, detail="Source not found")
        return updated
        
    # TODO: Реализовать обновление остальных полей
    raise HTTPException(status_code=501, detail="Update of other fields not implemented yet")





