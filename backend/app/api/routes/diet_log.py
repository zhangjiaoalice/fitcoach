from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.diet_log import DietLogOut, DietLogUpdate, DietLogCreate
from app.models.user import User
from app.services import diet_log_service
from typing import List

router = APIRouter(prefix="/diet-logs", tags=["diet-logs"])

@router.get("", response_model=List[DietLogOut])
async def list_diet_log(log_date: date, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    diet_log = await diet_log_service.list_diet_log(db, current_user.id, log_date)
    return diet_log

@router.post("", response_model=DietLogOut)
async def create_diet_log(log_data: DietLogCreate, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    diet_log = await diet_log_service.create_diet_log(db, current_user.id, log_data)
    return diet_log

@router.put("/{diet_id}", response_model=DietLogOut)
async def update_diet_log(diet_id: int, data: DietLogUpdate, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    try:
        diet_log = await diet_log_service.update_diet_log(db, current_user.id, diet_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return diet_log

# 删除成功用 204 是惯例
@router.delete("/{diet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet_log(diet_id: int, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    try:
        await diet_log_service.delete_diet_log(db, current_user.id, diet_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))