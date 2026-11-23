"""
工具： 记录一次饮水
用户说“刚喝了500ml的水” “帮我记录饮水” 时调用
"""
from datetime import date
from typing import Any

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import water_log_service
from app.schemas.water_log import CreateWaterLog


async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    arguments 来自LLM,含：
        log_date(str, 可选,没给默认今天)
        ml(int, 必填, 毫升数)
        source(str, 可选, white_water/tea/coffee/juice)
        note(str, 可选)
    """
    # 参数解析
    log_date_str = arguments.get("log_date") or date.today().isoformat()
    try: 
        data = CreateWaterLog(
            log_date = date.fromisoformat(log_date_str),
            ml=arguments["ml"],
            source=arguments.get("source"),
            note=arguments.get("note")
        ) 
    except (KeyError, ValueError) as e:
        return {"error": f"参数不完整或格式错: {e}"}


    # 调service落库
    water_log = await water_log_service.create_water_log(db=ctx.db, user_id=ctx.current_user.id, data=data)

    # 返回LLM 结构化结果（它回告诉用户已经记录）
    return {
        "id": water_log.id,
        "log_date": water_log.log_date.isoformat(),
        "ml": water_log.ml,
        "source": water_log.source,
        "note": water_log.note,
        "message": f"已帮你记录{water_log.ml}ml 饮水",
    }


log_water = Tool(
    name="log_water",
    description=(
        "记录一次饮水"
        "用户说“刚喝了500ml的水” “帮我记录饮水” 时调用"
        "参数："
        "  - log_date: 记录日期 (可选, 没给默认今天)"
        "  - ml: 毫升数 (必填)"
        "  - source: 饮水来源 (可选, white_water/tea/coffee/juice)"
        "  - note: 备注 (可选)"
    ),
    parameters={
        "type": "object",
        "properties": {
            "log_date": {
                "type": "string",
                "description": "记录日期,YYYY-MM-DD 格式,用户没指定就用今天",
            },
            "ml": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5000,
                "description": "饮水毫升数，如500",
            },
            "source": {
                "type": "string",
                "description": "饮水来源,white_water/tea/coffee/juice",
            },
            "note": {
                "type": "string",
                "description": "备注",
            },
        },
        "required": ["ml"],
    },
    handler=_handler
)

register_tool(log_water)