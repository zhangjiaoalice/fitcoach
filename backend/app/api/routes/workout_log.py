from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.schemas.workout_log import WorkoutLogOut, UpdateWorkoutLog, CreateWorkoutLog
from app.models.user import User
from app.api.deps import get_current_user
from app.db.session import get_db
from app.services import workout_log_service

router = APIRouter(prefix="/workout-logs", tags=["workout-logs"])

@router.get("", response_model=List[WorkoutLogOut])
async def get_workout_logs(log_date: date, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    workout_logs = await workout_log_service.list_workout_log(db, current_user.id, log_date)
    return workout_logs

@router.post("", response_model=WorkoutLogOut)
async def create_workout_log(log_data: CreateWorkoutLog, current_user: User=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        workout_log = await workout_log_service.create_workout_log(db, current_user.id, log_data)
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=str(e))
    return workout_log

@router.put("/{workout_log_id}")
async def update_workout_log(workout_log_id: int, log_data: UpdateWorkoutLog, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    try:
        workout_log = await workout_log_service.update_workout_log(db, current_user.id, workout_log_id, log_data)
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=str(e))
    return workout_log


@router.delete("/{workout_log_id}")
async def delete_workout_log(workout_log_id: int, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    try:
        await workout_log_service.delete_workout_log(db, current_user.id, workout_log_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))