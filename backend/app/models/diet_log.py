"""
ORM 模型： 将数据库表映射成 python 类，一张表就是一个类
"""
from datetime import date, datetime

from sqlalchemy import String, ForeignKey, Date, Integer, Numeric, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from app.db.session import Base

class DietLog(Base):
    # 表名
    __tablename__ = "diet_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    # 日志时间（使用date只包含时间）
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    # 早餐/午餐/晚餐
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 食物名称
    food_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # 量
    amount_text: Mapped[str | None] = mapped_column(String(100))
    # 热量
    calories_kcal: Mapped[int | None] = mapped_column(Integer) 
    # 蛋白质
    protein_g: Mapped[Decimal | None] = mapped_column(Numeric(6, 2),)
    # 碳水
    carbs_g: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    # 脂肪
    fat_g: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    # 原始自然语言输入
    raw_text: Mapped[str | None] = mapped_column(Text)
    # manual/agent
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    # 创建时间，带时区时间戳，默认now
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())