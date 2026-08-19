from pydantic import BaseModel, ConfigDict

from datetime import date, datetime
from decimal import Decimal

class CreateWeightLog(BaseModel):
    log_date: date
    weight: Decimal
    waist_cm: Decimal | None = None
    note: str | None = None


class UpdateWeightLog(BaseModel):
    log_date: date | None = None
    weight: Decimal | None = None
    waist_cm: Decimal | None = None
    note: str | None = None

class WeightLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    log_date: date
    weight: Decimal
    waist_cm: Decimal | None = None
    note: str | None = None
    created_at: datetime