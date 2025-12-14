from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...storage.database import get_db
from ...storage.repositories.filters import FilterRepository
from ..schemas import FilterCreate, FilterResponse, FilterUpdate

router = APIRouter(prefix="/filters", tags=["filters"])

@router.post("/", response_model=FilterResponse, status_code=status.HTTP_201_CREATED)
async def create_filter(filter_data: FilterCreate, db: AsyncSession = Depends(get_db)):
    repo = FilterRepository(db)
    # Проверяем существование
    if await repo.get_by_id(filter_data.id):
        raise HTTPException(status_code=400, detail="Filter with this ID already exists")
    
    return await repo.create(filter_data.model_dump())

@router.get("/", response_model=List[FilterResponse])
async def list_filters(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = FilterRepository(db)
    return await repo.list_all(skip, limit)

@router.get("/{filter_id}", response_model=FilterResponse)
async def get_filter(filter_id: str, db: AsyncSession = Depends(get_db)):
    repo = FilterRepository(db)
    filter_obj = await repo.get_by_id(filter_id)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")
    return filter_obj

@router.put("/{filter_id}", response_model=FilterResponse)
async def update_filter(filter_id: str, filter_data: FilterUpdate, db: AsyncSession = Depends(get_db)):
    repo = FilterRepository(db)
    # Удаляем None значения
    update_data = filter_data.model_dump(exclude_unset=True)
    updated_filter = await repo.update(filter_id, update_data)
    if not updated_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    return updated_filter

@router.delete("/{filter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_filter(filter_id: str, db: AsyncSession = Depends(get_db)):
    repo = FilterRepository(db)
    if not await repo.delete(filter_id):
        raise HTTPException(status_code=404, detail="Filter not found")





