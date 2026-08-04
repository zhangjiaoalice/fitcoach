"""
fastapi 应用入口
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Fitcoach] 应用启动")
    yield
    print("[Fitcoach] 应用关闭")

app = FastAPI(
    title="FitCoach Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 访问根路径，返回服务器信息
@app.get("/")
async def root():
    return {"service": "FitCoach Agent API", "status": "ok"}

# 接口健康检查
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    resp = await db.execute(text("SELECT 1"))
    if resp.fetchone():
        return {"status": "ok", "db": "connected"}
    else:
        return {"status": "error", "db": "disconnected"}