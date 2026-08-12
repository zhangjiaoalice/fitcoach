"""
认证路由层
route 层职责： 接收 HTTP 请求 -> 调service -> 返回响应，不写业务逻辑
几个 FastAPI 关键点:
- APIRouter: 把一组相关接口打包，最后在main.py 里 include 进来
- response_model=UserOut: FastAPI 会用 UserOut 过滤返回字段（自动去掉密码）
- status_code = 201: 注册成功， 用 201 Created 更规范
- Depends(get_db): 注入数据库会话
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, UserLogin,Token
from app.services import auth_service

# prefix="/auth" 这组都以 /auth 开头；tags 用于文档分组
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """注册： 交给service处理，捕获重复邮箱错误转成 400"""
    try:
        user = await auth_service.create_user(db, data)
    except ValueError as e:
        # service 抛的“邮箱已注册” 在这里转成标准的HTTP 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession=Depends(get_db)):
    """登录校验：校验登录邮箱-签发jwt, 失败转401"""
    try:
        user = await auth_service.authenticate_user(db, data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)