from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal


class DietSummary(BaseModel):
    """Diet summary schema"""
    kcal: Decimal
    meal_count: int


class WorkoutSummary(BaseModel):
    done: int
    total: int
    est_kcal: Decimal

class WaterSummary(BaseModel):
    """Water summary schema"""
    ml: Decimal
    target_ml: int

class WeightSummary(BaseModel):
    latest_kg: Decimal
    measured_at: date


class SleepSummary(BaseModel):
    duration_min: int
    slept_at: datetime | None

class RecordSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # optional 允许前端 ?. 安全访问
    diet: DietSummary | None = None
    workout: WorkoutSummary | None = None
    water: WaterSummary | None = None
    weight: WeightSummary | None = None
    sleep: SleepSummary | None = None
