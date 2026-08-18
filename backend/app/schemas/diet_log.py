from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal

class DietLogCreate(BaseModel):
    """接收前端提交的饮食日志字段"""
    log_date: date
    meal_type: str
    food_name: str
    source: str # manual/agent
    amount_text: str | None = None
    calories_kcal: int | None = None
    protein_g: Decimal | None = None
    carbs_g: Decimal | None = None
    fat_g: Decimal | None = None
    raw_text: str | None = None


class DietLogUpdate(BaseModel):
    """接收前端提交的更新字段"""
    log_date: date | None = None
    meal_type: str | None = None
    food_name: str | None = None
    source: str | None = None    # manual/agent
    amount_text: str | None = None
    calories_kcal: int | None = None
    protein_g: Decimal | None = None
    carbs_g: Decimal | None = None
    fat_g: Decimal | None = None
    raw_text: str | None = None


class DietLogOut(BaseModel):
    """返回给前端的饮食日志"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    log_date: date
    meal_type: str
    food_name: str
    source: str # manual/agent
    amount_text: str | None = None
    calories_kcal: int | None = None
    protein_g: Decimal | None = None
    carbs_g: Decimal | None = None
    fat_g: Decimal | None = None
    raw_text: str | None = None
    created_at: datetime
