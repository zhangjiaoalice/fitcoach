from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.agent.loop import run_agent
from app.agent.tools.base import AgentContext
from app.services import agent_service
from app.models.user import User

router = APIRouter(prefix="/agent", tags=["agent"])

class ChatIn(BaseModel):
    """前端发来的对话请求"""
    message: str

class ChatOut(BaseModel):
    """返回给前端的回复"""
    reply: str
    iterations: int
    tool_calls: list[dict] | None = None

@router.post("/chat", response_model=ChatOut)
async def chat(data: ChatIn, current_user: User=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ctx = AgentContext(db = db, current_user = current_user)

    try:
        result = await run_agent(data.message, ctx)
    except Exception as e:
        # 出错也要记trace
        await agent_service.save_trace(db, current_user.id, data.message, reply=None, iterations=0, tool_calls=None, error=str(e))
        raise HTTPException(status_code=500, detail=f"Agent 执行失败： {e}")

    # 记trace
    await agent_service.save_trace(
        db,
        current_user.id,
        data.message,
        reply=result["reply"],
        iterations=result["iterations"],
        tool_calls=result["tool_calls"],
    )

    return ChatOut(**result)