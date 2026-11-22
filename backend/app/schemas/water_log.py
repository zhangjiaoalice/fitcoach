from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal


class CreateWaterLog(BaseModel):
    log_date: date
    ml: int
    source: str | None = None
    note: str | None = None


class UpdateWaterLog(BaseModel):
    log_date: date | None = None
    ml: int | None = None
    source: str | None = None
    note: str | None = None

class WaterLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    log_date: date
    ml: int
    source: str | None = None
    note: str | None = None
    