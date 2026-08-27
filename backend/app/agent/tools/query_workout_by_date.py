"""
工具：查询用户某一天的训练计划
"""
from typing import Any
from datetime import date

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import workout_log_service

async def _handler(arguments: Any, ctx: AgentContext) -> dict[str, Any]:
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
                "intensity": log.intensity,
                "note": log.note,
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
                "description": "查询日期， YYYY-MM-DD 格式，如 2026-08-26，如果用户没有指定日期，则使用今天"
            },
        },
        "required": ["log_date"]
    },
    handler=_handler,
)

register_tool(query_workout_by_date)