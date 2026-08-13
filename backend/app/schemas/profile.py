from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class ProfileUpsert(BaseModel):
    """接收前端提交的用户画像"""
    gender: str | None = None # 前端可以不传这个字段
    age: int
    height_cm: int
    current_weight_kg: Decimal
    target_weight_kg: Decimal
    activity_level: str
    training_days_per_week: int
    diet_preference: str | None = None
    health_notes: str | None = None
    goal_description: str | None = None

class ProfileOut(BaseModel):
    """返回给前端的用户画像"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    gender: str | None
    age: int
    height_cm: int
    current_weight_kg: Decimal
    target_weight_kg: Decimal
    activity_level: str
    training_days_per_week: int
    diet_preference: str | None
    health_notes: str | None
    goal_description: str | None
    created_at: datetime

