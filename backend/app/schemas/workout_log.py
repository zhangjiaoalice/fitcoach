from pydantic import BaseModel, ConfigDict

from datetime import date, datetime

class CreateWorkoutLog(BaseModel):
    workout_type: str
    duration_min: int
    intensity: str
    log_date: date
    note: str | None = None

class UpdateWorkoutLog(BaseModel):
    workout_type: str | None = None
    duration_min: int | None = None
    intensity: str | None = None
    note: str | None = None
    log_date: date | None = None

class WorkoutLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True) # 从orm对象中读取字段
    id: int
    user_id: int
    workout_type: str
    duration_min: int
    intensity: str
    log_date: date
    created_at: datetime
    note: str | None = None