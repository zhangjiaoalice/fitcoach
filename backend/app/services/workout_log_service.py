from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.schemas.workout_log import CreateWorkoutLog, UpdateWorkoutLog
from app.models.workout_log import WorkoutLog
from typing import List

async def create_workout_log(db: AsyncSession, user_id: int, data: CreateWorkoutLog):
    workout_log = WorkoutLog(user_id=user_id, **data.model_dump())
    db.add(workout_log)
    await db.commit()
    await db.refresh(workout_log)
    return workout_log

# list 不会返回None，.all 为空时返回 []
async def list_workout_log(db: AsyncSession, user_id: int, log_date: date) -> List[WorkoutLog]:
    stmt = select(WorkoutLog).where(WorkoutLog.user_id == user_id, WorkoutLog.log_date == log_date)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_workout_log(db: AsyncSession, user_id: int, workout_log_id: int):
    stmt = select(WorkoutLog).where(WorkoutLog.user_id == user_id, WorkoutLog.id == workout_log_id)
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    if not row:
        raise ValueError("No workout log found for the given user and workout id")
    return row

async def update_workout_log(db: AsyncSession, user_id: int, workout_log_id: int, data: UpdateWorkoutLog):
    workout_log = await get_workout_log(db, user_id, workout_log_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(workout_log, k, v)
    await db.commit()
    await db.refresh(workout_log)
    return workout_log

async def delete_workout_log(db: AsyncSession, user_id: int, workout_log_id: int):
    workout_log = await get_workout_log(db, user_id, workout_log_id)
    await db.delete(workout_log)
    await db.commit()