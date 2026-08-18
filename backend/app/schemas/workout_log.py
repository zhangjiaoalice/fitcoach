from pydantic import BaseModel, ConfigDict

from datetime import date, datetime

class CreateWorkoutLog(BaseModel):
    workout_type: str
    duration_time: int
    intensity: str
    note: str | None = None
    log_date: date | None = None

class UpdateWorkoutLog(BaseModel):
    workout_type: str | None = None
    duration_time: int | None = None
    intensity: str | None = None
    note: str | None = None
    log_date: date | None = None

class WorkoutLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True) # 从orm对象中读取字段
    id: int
    user_id: int
    workout_type: str
    duration_time: int
    intensity: str
    note: str | None = None
    log_date: date | None = None
    created_at: datetime