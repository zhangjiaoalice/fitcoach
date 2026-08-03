"""FastAPI 应用入口。

【这个文件是你的练习#2】

M0 阶段目标：让应用能启动，并且有一个 /health 接口能确认数据库真的连通了。
这是所有后端项目的第一块试金石——先证明"应用能跑 + 能连库"，再谈业务。

后续里程碑会在这里 include 各个模块的路由（认证、画像、记录……），
现在先把地基打通。
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行 yield 之前的代码，关闭时执行之后的。
    # 现在先留空，M2 起可以在这里做建表 / 预热等。
    print("[FitCoach] 应用启动")
    yield
    print("[FitCoach] 应用关闭")


app = FastAPI(
    title="FitCoach Agent API",
    version="0.1.0-M0",
    lifespan=lifespan,
)

# CORS：允许前端(Vite 默认 5173)跨域访问。基建，AI 已配好。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"service": "FitCoach Agent", "status": "ok"}


# ─────────────────────────────────────────────────────────
# TODO #1: 实现健康检查接口 /health
# 要求：不仅返回 ok，还要真正查一下数据库（否则"假健康"）。
# 提示：
#   1. 这个函数用 Depends(get_db) 注入一个 db 会话（就是你在 session.py 写的）
#   2. 执行一条最简单的 SQL：await db.execute(text("SELECT 1"))
#   3. 成功就返回 {"status": "ok", "db": "connected"}
# 函数签名参考：
#   async def health(db: AsyncSession = Depends(get_db)):
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    # TODO: 执行 SELECT 1 验证数据库连通，返回连通状态
    raise NotImplementedError("请实现 health 检查")
