from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.models.agent_traces import AgentTrace

async def save_trace(
        db: AsyncSession,
        user_id: int,
        user_message: str,
        reply: str | None,
        iterations: int,
        tool_calls: list | None,
        error: str | None = None
) -> None:
    trace = AgentTrace(
        user_id = user_id,
        user_message = user_message,
        reply = reply,
        iterations = iterations,
        tool_calls_json = json.dumps(tool_calls, ensure_ascii=False, default=str) if tool_calls else None,
        error = error
    )
    db.add(trace)
    await db.commit()
    await db.refresh(trace)