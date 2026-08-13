"""
用户画像表模型
"""
from datetime import datetime
from sqlalchemy import DateTime, String, func, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from app.db.session import Base

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True, nullable=False)

    gender: Mapped[str | None] = mapped_column(String(10))

    age: Mapped[int] = mapped_column(Integer, nullable=False)

    height_cm: Mapped[int] = mapped_column(Integer, nullable=False)

    # 最多 5 位, 保留2位小数, 如： 168.50, Decimal 对象（高精度）
    current_weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2),nullable=False)

    # 目标体重，最多 5 位, 保留2位小数, 如： 168.50
    target_weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2),nullable=False)

    # 活动水平
    activity_level: Mapped[str] = mapped_column(String(10), nullable=False)

    # 每周训练天数
    training_days_per_week: Mapped[int] = mapped_column(Integer, nullable=False)

    # 饮食偏好
    diet_preference: Mapped[str] = mapped_column(String(255), nullable=True)

    # 健康备注
    health_notes: Mapped[str] = mapped_column(String(255), nullable=True)

    #  目标描述
    goal_description: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
