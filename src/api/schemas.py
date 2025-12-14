from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FilterBase(BaseModel):
    id: str
    name: str
    prompt: str
    categories: List[str]
    threshold: float = 0.7
    enabled: bool = True

class FilterCreate(FilterBase):
    pass

class FilterUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    categories: Optional[List[str]] = None
    threshold: Optional[float] = None
    enabled: Optional[bool] = None

class FilterResponse(FilterBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    type: str = Field(..., pattern="^(telegram|vk)$")
    source_id: str
    name: Optional[str] = None
    enabled: bool = True
    check_interval: int = 60

class SourceCreate(SourceBase):
    filter_ids: List[str] = []

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    check_interval: Optional[int] = None
    filter_ids: Optional[List[str]] = None

class SourceResponse(SourceBase):
    id: int
    created_at: datetime
    filters: List[FilterResponse] = []

    class Config:
        from_attributes = True





