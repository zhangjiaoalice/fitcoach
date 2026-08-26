"""
工具：查询用户某一天的训练计划
"""
from typing import Any
from datetime import date

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import workout_log_service

async def _handler(arguments: Any, ctx: AgentContext) -> list[str, Any]:
    """
    arguments: LLM 传的参数
    ctx: Agent 上下文，包含 db 和 current_user
    """
    log_date = date.fromisoformat(arguments["log_date"])

    workout_logs = await workout_log_service.list_workout_log(ctx.db, ctx.current_user.id, log_date)

    return {
        "count": len(workout_logs),
        "logs": [
            {
                "workout_type": log.workout_type,
                "duration_min": log.duration_min,
                "intensity": log.intensity if log.intensity is not None else None,
                "note": log.note if log.note is not None else None,
            } for log in workout_logs
        ]
    }

query_workout_by_date = Tool(
    name="query_workout_by_date",
    description="查询用户某一天的训练计划。当用户询问'我今天训练了什么/昨天训练了多长时间'时调用",
    parameters={
        "type": "object",
        "properties": {
            "log_date": {
                "type": "string",
                "format": "date",
            },
        },
    },
    handler=_handler,
)

register_tool(query_workout_by_date)