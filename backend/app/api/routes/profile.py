from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.schemas.profile import ProfileUpsert, ProfileOut
from app.models.user import User
from app.db.session import get_db
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("", response_model=ProfileOut)
async def get_profile(current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    profile = await profile_service.get_profile(db, current_user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="画像未创建")
    return profile

@router.put("", response_model=ProfileOut)
async def update_profile(data: ProfileUpsert, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    profile = await profile_service.upsert_profile(db, current_user.id, data)
    return profile