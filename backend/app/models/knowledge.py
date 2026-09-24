"""
RAG 知识库：存储切片后的健身知识 + 向量
这个表是全局共享，不属于某个 user_id
"""
from datetime import datetime
from typing import Any

from sqlalchemy import String, Integer, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector # 向量列类型

from app.db.session import Base

class Knowledge(Base):
    __tablename__ = "knowledge"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 标题
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # 来源
    source: Mapped[str] = mapped_column(String(255), nullable=False)

    # 正文
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # embedding 向量
    embedding: Mapped[list[float]] = mapped_column(Vector(1024), nullable=False)

    # 为空表示未统计token
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
