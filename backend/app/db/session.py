"""
数据库连接与会话管理
- Engine(引擎)：数据库连接池总管，整个应用只需要一个
- Session(会话)： 一次数据库交互上下文，每个请求用一个，用完关闭, 维持会话状态并与数据库交互
- Base: 所有 ORM 模型的基类，每个模型都会继承它
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

# 获取全局配置
settings = get_settings()

class Base(DeclarativeBase):
    """所有 ORM 模型的基类， 每个表都会继承它， pass表示空类"""
    pass

# 创建异步引擎
# echo - 是否打印SQL语句（开发阶段，方便调试）
# pool_pre_ping - 是否在每次使用连接前检查连接是否有效
engine = create_async_engine(settings.database_url, echo=True, pool_pre_ping=True)

# 创建session工厂
# expire_on_commit - 是否在每次提交后自动清理session
# class_ - 指定session的类型为AsyncSession
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# get_db 依赖，FastAPI 每次请求会调用它拿到一个session，请求结束会自动关闭（依赖注入）
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session