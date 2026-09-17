"""
工具： 记录一条训练日志
让 Agent 能以自然语言帮用户记录
"""
from datetime import date
from typing import Any

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import workout_log_service
from app.schemas.workout_log import CreateWorkoutLog

async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    arguments 来自LLM, 含：
        log_date(str, 必填 YYYY-MM-DD)
        workout_type(str, 必填 如 ‘力量’、‘有氧’、‘HIT’)
        duration_min(int, 必填 训练时长 单位：分钟)
        intensity(str, 必填 低/中/高)
        note(str, 可选 备注信息)
    """
    try:
        data = CreateWorkoutLog(
            log_date=date.fromisoformat(arguments["log_date"]),
            workout_type=arguments["workout_type"],
            duration_min=arguments["duration_min"],
            intensity=arguments["intensity"],
            note=arguments.get("note"),
        )
    except (KeyError, ValueError) as e:
        return {"error": f"参数不完整或格式错误：{e}"}

    workout_log = await workout_log_service.create_workout_log(db=ctx.db, user_id=ctx.current_user.id, data=data)

    return {
        "id": workout_log.id,
        "log_date": workout_log.log_date.isoformat(),
        "workout_type": workout_log.workout_type,
        "duration_min": workout_log.duration_min,
        "intensity": workout_log.intensity,
        "message": f"已帮你记录{workout_log.workout_type} {workout_log.duration_min}分钟"
    }


log_workout=Tool(
    name="log_workout",
    description=(
        "记录用户某天（默认今天）的一次训练。"
        "当用户说'帮我记训练'、'我今天练了xxx'、'跑了30分钟'时调用。"
        "必需信息：日期(YYYY-MM-DD, 用户没说默认用今天)、训练类型(如力量/有氧/HIIT/瑜伽/普拉提等自由文本)、时长(分钟)、强度(高/中/低)。"
        "可选: 备注(note)。用户没明确说明强度就问一下,或默认'中'。"
    ),
    parameters={
        "type": "object",
        "properties": {
            "log_data": {
                "type": "string",
                "description": "记录日期， YYYY-MM-DD 格式，用户没指定就用今天"
            },
            "workout_type": {
                "type": "string",
                "description": "训练类型， 自由文本，如： ‘力量’、‘有氧’、‘HIT’、‘瑜伽’、‘普拉提’、‘跑步’、‘游泳’"
            },
            "duration_min": {
                "type": "integer",
                "minimum": 0,
                "description": "训练时长，单位：分钟，必须大于0"
            },
            "intensity": {
                "type": "string",
                "enum": ["低", "中", "高"],
                "description": "训练强度，低/中/高， 没说默认为中",
            },
            "note": {
                "type": "string",
                "description": "备注， 如具体动作，组数，感受"
            }
        },
        "required": ["log_date", "workout_type", "duration_min", "intensity"]
    },
    handler=_handler
)

register_tool(log_workout)
