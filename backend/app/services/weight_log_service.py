from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import List

from app.models.weight_log import WeightLog
from app.schemas.weight_log import CreateWeightLog, UpdateWeightLog, WeightLogOut
from app.models.user import User

async def create_weight_log(db: AsyncSession, user_id: int, data: CreateWeightLog):
    weight_log = WeightLog(user_id=user_id, **data.model_dump())
    db.add(weight_log)
    await db.commit()
    await db.refresh(weight_log)
    return weight_log

async def list_weight_log(db: AsyncSession, user_id: int, log_date: date) -> List[WeightLogOut]:
    stmt = select(WeightLog).where(User.id == user_id, WeightLog.log_date == log_date)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_weight_log(db: AsyncSession, user_id: int, weight_log_id: int) -> WeightLogOut:
    stmt = select(WeightLog).where(User.id == user_id, WeightLog.id == weight_log_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_weight_log(db: AsyncSession, user_id: int, weight_log_id: int, data: UpdateWeightLog):
    weight_log = await get_weight_log(db, user_id, weight_log_id)
    if not weight_log:
        raise ValueError("未找到体重记录日志")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(weight_log, k, v)

    await db.commit()
    await db.refresh(weight_log)
    return weight_log

async def delete_weight_log(db: AsyncSession, user_id: int, weight_log_id: int):
    weight_log = await get_weight_log(db, user_id, weight_log_id)
    if not weight_log:
        raise ValueError("未找到体重记录日志")
    db.delete(weight_log)
    await db.commit()