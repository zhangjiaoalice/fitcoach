"""
定义 体重记录 orm 模型
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Integer, Date, DateTime, ForeignKey, Numeric, func
from datetime import date, datetime
from decimal import Decimal

from app.db.session import Base

class WeightLog(Base):
    __tablename__ = "weight-logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    waist_cm: Mapped[Decimal | None] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

