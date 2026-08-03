"""数据库连接与会话管理（SQLAlchemy 2.0 异步）。

【这个文件是你的练习#1】

背景知识（先读懂再动手）：
- Engine（引擎）：数据库连接池的总管，整个应用只需要一个。
- Session（会话）：一次数据库交互的上下文，每个请求用一个、用完就关。
- Base：所有 ORM 模型的基类，M2 起你写的每个表模型都会继承它。

异步版和你熟悉的同步写法的区别：
- 用 create_async_engine 而不是 create_engine
- 用 AsyncSession 而不是 Session
- 增删改查都要 await

FastAPI 里的用法（M1起会看到）：
    async def some_route(db: AsyncSession = Depends(get_db)):
        ...
get_db 是一个"依赖"，FastAPI 每次请求会调用它拿到一个 session，
请求结束自动关闭——这就是依赖注入，后端最重要的模式之一。
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。M2 起你的每个表都继承它。"""
    pass


# ─────────────────────────────────────────────────────────
# TODO #1: 创建异步引擎
# 提示：用 create_async_engine，第一个参数是 settings.database_url。
#       建议加 echo=True（开发期把SQL 打到控制台，方便你观察 ORM 生成的语句）。
# 参考签名：create_async_engine(url, echo=..., pool_pre_ping=True)
#pool_pre_ping=True 表示取连接前先 ping 一下，避免拿到已断开的死连接。
# engine = ...
engine = None  # ← 替换成你的实现


# ─────────────────────────────────────────────────────────
# TODO #2: 创建会话工厂
# 提示：用 async_sessionmaker，绑定上面的 engine。
#       常用参数：bind=engine, expire_on_commit=False, class_=AsyncSession
#       expire_on_commit=False 让对象 commit 后仍可访问属性（否则会触发额外查询）。
# AsyncSessionLocal = ...
AsyncSessionLocal = None  # ← 替换成你的实现


# ─────────────────────────────────────────────────────────
# TODO #3: 实现 get_db 依赖
# 这是一个异步生成器：yield 出一个 session 给路由用，路由结束后自动关闭。
# 提示结构：
#   async with AsyncSessionLocal() as session:
#       yield session
# 为什么用 async with？它保证无论请求成功或异常，session 都会被正确关闭。
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # TODO: 用 async with 打开一个 session 并 yield 出去
    raise NotImplementedError("请实现 get_db")
