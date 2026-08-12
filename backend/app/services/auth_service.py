"""认证业务逻辑（service层）"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """按 email 查用户，查不到返回 None"""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """注册： 查重 -> 哈希 -> 存库"""
    existing = await get_user_by_email(db, data.email)
    if existing is not None:
        raise ValueError("该邮箱已被注册")

    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """登录校验：查用户 -> 比对密码，失败抛出 ValueError"""
    user = await get_user_by_email(db, email)
    # 关键： 用户不存在或者 密码错误，都返回童颜的错误，不告诉攻击者“是账号错还是密码错”
    if user is None or not verify_password(password, user.hashed_password):
        raise ValueError("邮箱或密码错误")
    return user