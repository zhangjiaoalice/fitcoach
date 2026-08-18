"""
定义 训练记录 ORM 模型
"""
from sqlalchemy import String, Integer, ForeignKey, Date, Datetime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime

from app.db.session import Base

class WorkoutLog(Base):
    __tablenames__ = "workout_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    log_date: Mapped[date] | None = mapped_column(ForeignKey("diet_logs.log_date"), nullable=True)
    workout_type: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_time: Mapped[int] = mapped_column(Integer, nullable=False)
    intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str] | None = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] | None = mapped_column(Datetime(timezone=True), nullable=True, server_default=func.now())    