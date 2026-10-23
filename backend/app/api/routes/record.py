
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.record import RecordSummary

from app.db.session import get_db
from app.api.deps import get_current_user
import app.services.record_service as record_service

router = APIRouter(prefix="/record", tags=["record"])

@router.get("/summary", response_model=RecordSummary)
async def get_summary(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await record_service.get_record_summary(db, current_user.id)