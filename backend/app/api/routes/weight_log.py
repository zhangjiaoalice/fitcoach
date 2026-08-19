from fastapi import APIRouter, Depends ,HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.weight_log import CreateWeightLog, UpdateWeightLog, WeightLogOut
from app.services import weight_log_service

router = APIRouter(prefix="/weight-logs", tags=["weight-logs"])

@router.get("", response_model=List[WeightLogOut])
async def get_weight_logs(log_date: date, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    weight_logs = await weight_log_service.list_weight_log(db, current_user.id, log_date)
    return weight_logs

@router.post("", response_model=WeightLogOut)
async def create_weight_log(data: CreateWeightLog, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    weight_log = await weight_log_service.create_weight_log(db, current_user.id, data)
    return weight_log

@router.put("/{weight_log_id}", response_model=WeightLogOut)
async def update_weight_log(weight_log_id: int, data: UpdateWeightLog, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    try:
        weight_log = await weight_log_service.update_weight_log(db, current_user.id, weight_log_id, data)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=str(e))
    return weight_log

@router.delete("/{weight_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weight_log(weight_log_id: int, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    try:
        await weight_log_service.delete_weight_log(db, current_user.id, weight_log_id)
    # except Exception 把数据库错、代码 bug 等都当成 404,会掩盖真实问题,用 ValueError catch 真实错误
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=str(e))