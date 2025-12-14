from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
from .database import Base

# Таблица связи many-to-many для источников и фильтров
source_filters = Table(
    "source_filters",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("sources.id"), primary_key=True),
    Column("filter_id", String, ForeignKey("filters.id"), primary_key=True),
)


class Filter(Base):
    """Модель фильтра для AI анализа"""
    __tablename__ = "filters"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # Уникальный ID (например, 'tech_news')
    name: Mapped[str] = mapped_column(String, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    categories: Mapped[list] = mapped_column(JSON, nullable=False)  # Список категорий
    threshold: Mapped[float] = mapped_column(Float, default=0.7)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Связи
    sources: Mapped[List["Source"]] = relationship(
        secondary=source_filters,
        back_populates="filters"
    )

    def __repr__(self):
        return f"<Filter(id='{self.id}', name='{self.name}')>"


class Source(Base):
    """Модель источника постов (Telegram канал или VK группа)"""
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'telegram' или 'vk'
    source_id: Mapped[str] = mapped_column(String, nullable=False)  # ID канала/группы (@channel или -12345)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    check_interval: Mapped[int] = mapped_column(Integer, default=60)  # Интервал проверки в секундах
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    filters: Mapped[List["Filter"]] = relationship(
        secondary=source_filters,
        back_populates="sources"
    )

    def __repr__(self):
        return f"<Source(type='{self.type}', id='{self.source_id}')>"


class ProcessedPost(Base):
    """Модель обработанного поста (для истории и дедупликации)"""
    __tablename__ = "processed_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[str] = mapped_column(String, nullable=False)
    post_id: Mapped[str] = mapped_column(String, nullable=False)  # ID поста в источнике
    
    text_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=True)  # MD5 хеш текста для дедупликации
    
    filter_result: Mapped[dict] = mapped_column(JSON, nullable=True)  # Полный ответ AI
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    was_forwarded: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProcessedPost(source='{self.source_id}', post='{self.post_id}')>"





