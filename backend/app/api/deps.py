"""
API 依赖： 鉴权
get_current_user 是一个依赖，任何需要登录才能访问的接口，只要在参数中写 current_user = Depends(get_current_user),
FastAPI 就会自动跑这个依赖： 取token -> 验证 -> 查用户
验证不通过就直接返回 401，验证通过就把 User 对象交给接口
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录状态无效或已过期",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = await db.get(User, int(user_id))
    if user is None:
        raise credentials_error
    return user