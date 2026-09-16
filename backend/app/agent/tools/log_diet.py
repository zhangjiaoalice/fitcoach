"""
工具： 记录一条饮食日志
让 Agent 能以自然语言帮用户记录饮食（source="agent"）
"""
from datetime import date
from typing import Any

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import diet_log_service
from app.schemas.diet_log import DietLogCreate

async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    arguments 来自 LLM ， 含：
        log_date（str, 比填 YYYY-MM-DD）
        meal_type(str, 必填 breakfast、lunch、dinner、snack)
        food_name(str, 必填)
        amount_text / calories_kcal / protein_g / carbs_g/ fat_g / raw_text(str, 可选)
    source 由后端固定为 “agent”, 不让 LLM 传 
    """
    # 构造 DietLogCreate
    try:
        data = DietLogCreate(
            log_date=date.fromisoformat(arguments["log_date"]),
            meal_type=arguments["meal_type"],
            food_name=arguments["food_name"],
            source="agent",
            amount_text=arguments.get("amount_text"),
            calories_kcal=arguments.get("calories_kcal"),
            protein_g=arguments.get("protein_g"),
            carbs_g=arguments.get("carbs_g"),
            fat_g=arguments.get("fat_g"),
            raw_text=arguments.get("raw_text"),
        )
    except (KeyError, ValueError) as e:
        # 必填字段缺失或格式错 —— 返回错误让 LLM 自己告诉用户"我需要 XXX"
        return {"error": f"参数不完整或格式错: {e}"}


    # 调 service 落库
    diet_log = await diet_log_service.create_diet_log(db=ctx.db, user_id=ctx.current_user.id, data=data)

    # 返回LLM 结果（它回告诉用户已经记录）
    return {
        "id": diet_log.id,
        "log_date": diet_log.log_date.isoformat(),
        "meal_type": diet_log.meal_type,
        "food_name": diet_log.food_name,
        "amount_text": diet_log.amount_text,
        "calories_kcal": diet_log.calories_kcal,
        "message": f"已帮你记录{diet_log.meal_type} 的 {diet_log.food_name}"
    }

log_diet = Tool(
    name="log_diet",
    description=(
        "记录用户某天（默记今天）的一餐饮食。"
        "当用户说 '帮我记录饮食', '我今天午餐吃了 xxx', '记一下我早餐xxx' 时调用。"
        "必需信息: 日期(YYYY-MM-DD, 用户没说就用今天), 餐段(breakfast/lunch/dinner/snack)、食物名。"
        "可选信息: 分量文字（amount_text）、热量（calories_kcal, 整数）、蛋白/碳水/脂肪（g, 数字）、原话(raw_text)。"
        "用户没给营养数据就别瞎编，让字段为空即可"
    ),
    parameters={
        "type": "object",
        "properties": {
            "log_date": {
                "type": "string",
                "description": "记录日期， YYYY-MM-DD 格式，用户没制定默认用今天的日期",
            },
            "meal_type": {
                "type": "string",
                "enum": ["breakfast", "lunch", "dinner", "snack"],
                "description": "餐段: breakfast=早餐, lunch=午餐, dinner=晚餐, snack=加餐"
            },
            "food_name": {
                "type": "string",
                "description": "食物名称，如 '鸡胸肉', '西兰花', '白米饭'"
            },
            "amount_text": {
                "type": "string",
                "description": "份量，自由文本， 如 '150g', '一碗', '两片'"
            },
            "calories_kcal": {
                "type": "number",
                "minimum": 0,
                "description": "热量，单位千卡，如 150"
            },
            "protein_g": {
                "type": "number",
                "minimum": 0,
                "description": "蛋白质，单位克，如 15"
            },
            "carbs_g": {
                "type": "number",
                "minimum": 0,
                "description": "碳水，单位克，如 15"
            },
            "fat_g": {
                "type": "number",
                "minimum": 0,
                "description": "脂肪，单位克，如 15"
            },
            "raw_text": {
                "type": "string",
                "description": "用户的原话, 方便追溯"
            }
        },
        "required": ["log_date", "meal_type", "food_name"]
    },
    handler=_handler
)

register_tool(log_diet)