"""
工具: 查询用户体重趋势
"""
from typing import Any

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import weight_log_service

async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    arguments: LLM 调用工具时传的参数
    ctx: Agent 上下文，含db 和 user_id
    """
    days = arguments.get("days", 7)
    weight_logs = await weight_log_service.list_weight_recent(ctx.db, ctx.current_user.id, days)

    return {
        "count": len(weight_logs),
        "days_queried": days,
        "logs": [
            {
                "log_date": log.log_date.isoformat(),
                "weight_kg": float(log.weight_kg),
                "waist_cm": float(log.waist_cm) if log.waist_cm is not None else None,
                "note": log.note
            } for log in weight_logs
        ]
    }

query_weight_trend = Tool(
    name="query_weight_trend",
    description="查询用户最近 N 天的体重（和腰围）趋势。当用户询问'我最近瘦了多少/体重变化怎样/最近一周体重趋势'时调用。",
    parameters={
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "查询最近多少天，默认7天",
                "default": 7,
                "minimum": 1,
                "maximum": 70
            }
        },
        "required": []
    },
    handler=_handler
)

register_tool(query_weight_trend)