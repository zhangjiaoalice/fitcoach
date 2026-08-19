"""
定义 训练记录 ORM 模型
"""
from sqlalchemy import String, Integer, ForeignKey, Date, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime

from app.db.session import Base

class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    workout_type: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    intensity: Mapped[str | None] = mapped_column(String(20), nullable=True) # 训练强度 低/中/高
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())    