"""
工具: 记录一条体重日志。
让 Agent 能以自然语言帮用户记体重。
"""
from datetime import date
from typing import Any

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import weight_log_service
from app.schemas.weight_log import CreateWeightLog


async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    arguments 来自 LLM,含:
        log_date (str, 必填 YYYY-MM-DD)
        weight_kg (number, 必填 单位 kg)
        waist_cm (number, 可选 单位 cm)
        note (str, 可选)
    """
    try:
        data = CreateWeightLog(
            log_date=date.fromisoformat(arguments["log_date"]),
            weight_kg=arguments["weight_kg"],
            waist_cm=arguments.get("waist_cm"),
            note=arguments.get("note"),
        )
    except (KeyError, ValueError) as e:
        return {"error": f"参数不完整或格式错: {e}"}

    weight_log = await weight_log_service.create_weight_log(
        db=ctx.db, user_id=ctx.current_user.id, data=data
    )

    return {
        "id": weight_log.id,
        "log_date": weight_log.log_date.isoformat(),
        "weight_kg": float(weight_log.weight_kg),
        "waist_cm": float(weight_log.waist_cm) if weight_log.waist_cm is not None else None,
        "message": f"已帮你记录 {weight_log.log_date.isoformat()} 体重 {float(weight_log.weight_kg)} kg",
    }


log_weight = Tool(
    name="log_weight",
    description=(
        "记录用户某天(默认今天)的体重(和可选的腰围)。"
        "当用户说'帮我记体重'、'我今天 XX 公斤'、'称了一下 XX kg' 时调用。"
        "必需信息: 日期(YYYY-MM-DD,用户没说就用今天)、体重(kg)。"
        "可选: 腰围(cm)、备注。"
    ),
    parameters={
        "type": "object",
        "properties": {
            "log_date": {
                "type": "string",
                "description": "记录日期,YYYY-MM-DD 格式,用户没指定就用今天",
            },
            "weight_kg": {
                "type": "number",
                "minimum": 20,
                "maximum": 300,
                "description": "体重,单位 kg,如 68.5",
            },
            "waist_cm": {
                "type": "number",
                "minimum": 30,
                "maximum": 200,
                "description": "腰围,单位 cm,如 78",
            },
            "note": {
                "type": "string",
                "description": "备注,如'空腹'、'饭后'",
            },
        },
        "required": ["log_date", "weight_kg"],
    },
    handler=_handler,
)

register_tool(log_weight)