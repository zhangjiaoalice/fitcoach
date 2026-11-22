"""
定义 饮水记录 orm 模型
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Date, DateTime, ForeignKey, func, String
from datetime import date, datetime
from decimal import Decimal

from app.db.session import Base

class WaterLog(Base):
    __tablename__="water_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    ml: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str | None] = mapped_column(String(20), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())