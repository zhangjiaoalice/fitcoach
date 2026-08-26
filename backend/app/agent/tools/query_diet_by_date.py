"""
工具： 根据日期查询饮食记录
"""
from typing import Any
from datetime import date

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import diet_log_service

async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    真正执行的函数：
    - arguments： LLM 传的参数（这个工具无参数，忽略）
    - ctx: 含db和current_user
    """
    # LLM 传的事字符串，需要转成date对象再查
    log_date = date.fromisoformat(arguments["date"])
    # 获取饮食记录
    diet_logs = await diet_log_service.list_diet_log(ctx.db, ctx.current_user.id, log_date)

    # 将orm 对象转换成 JSON 可序列化的dict
    return {
        "count": len(diet_logs),
        "logs": [
            {
                "meal_type": log.meal_type,
                "food_name": log.food_name,
                "amount_text": log.amount_text,
                "calories_kcal": log.calories_kcal,
                "protein_g": float(log.protein_g) if log.protein_g is not None else None,
                "carbs_g": float(log.carbs_g) if log.carbs_g is not None else None,
                "fat_g": float(log.fat_g) if log.fat_g is not None else None,
                "raw_text": log.raw_text,
                "source": log.source,
            }
            for log in diet_logs
        ]
    }


query_diet_by_date = Tool(
    name="query_diet_by_date",
    description="查询用户某一天的饮食记录。当用户询问'我今天吃了什么/昨天摄入多少热量'时调用",
    parameters={
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "查询日期， YYYY-MM-DD 格式，如 2026-08-26，如果用户没有指定日期，则使用今天"
            }
        },
        "required": ["date"]
    },
    handler=_handler
)
register_tool(query_diet_by_date)