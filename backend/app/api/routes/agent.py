import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.agent.loop import run_agent, run_agent_stream
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

def __sse_pack(event: dict) -> str:
    """把dict 事件序列化 SSE 格式"""
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"

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

@router.post('/chat/stream')
async def chat_stream(data: ChatIn, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    """
    流式版本对话接口 - SSE
    前端用 fetch + ReadableStream 消费

    事件类型（和 loop.py yield 出来的一致）：
        delta/ tool_start/ tool_result/ done/ error
    """
    ctx = AgentContext(db = db, current_user = current_user)

    # 攒trace 需要的字段
    final_reply = ''
    final_iterations = 0
    final_tool_calls: list = []
    final_error: str | None = None

    async def event_stream():
        # nonlocal 是python的一个关键字，用来在嵌套函数中修改外层函数的变量，而不是全局变量
        nonlocal final_reply, final_iterations, final_tool_calls, final_error

        try:
            async for event in run_agent_stream(data.message, ctx):
                # 转发给前端
                yield __sse_pack(event)

                # 边推边攒信息用于trace
                if event["type"] == "done":
                    final_reply = event.get("reply", "")
                    final_iterations = event.get("iterations", 0)
                    final_tool_calls = event.get("tool_calls", [])
                elif event["type"] == "error":
                    final_error = event.get("message", "unknown")
        except Exception as e:
            final_error = f"stream 意外中断： {e}"
            yield __sse_pack({"type": "error", "message": final_error})
        finally:
            # 无论成功还是失败，写一条trace 落库
            try:
                await agent_service.save_trace(
                    db,
                    user_id=current_user.id,
                    user_message=data.message,
                    reply=final_reply,
                    iterations=final_iterations,
                    tool_calls=final_tool_calls,
                    error=final_error,
                )
            except Exception as e:
                # trace 写入失败， 不影响用户，只打印
                print(f"[trace 写入失败] {e}")
    return StreamingResponse(
            event_stream(), 
            media_type="text/event-stream",
            headers={
                # 关闭中间代理 nginx/中间代理的缓冲才能实时推
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )