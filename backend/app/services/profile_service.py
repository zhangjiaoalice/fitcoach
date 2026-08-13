from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.schemas.profile import ProfileUpsert


async def get_profile(db: AsyncSession, user_id: int) -> Profile | None:
    """根据user_id 查用户画像"""
    stmt= select(Profile).where(Profile.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_profile(db: AsyncSession, user_id: int, data: ProfileUpsert) -> Profile:
    """更新或创建用户画像"""
    profile = await get_profile(db, user_id)
    if profile is not None:
        # 更新已有对象要逐字段赋值
        for k, v in data.model_dump().items():
            setattr(profile, k, v)
    else:
        # 不存在，新建用户画像
        profile = Profile(user_id=user_id, **data.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile