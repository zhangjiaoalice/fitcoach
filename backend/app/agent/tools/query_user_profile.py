"""
工具： 查询用户的健康画像
让 Agent 根据用户的身高/年龄/体重/目标给出针对性的建议
"""
from typing import Any

from app.agent.tools.base import Tool, AgentContext, register_tool
from app.services import profile_service

async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    真正执行的函数：
    - arguments： LLM 传的参数（这个工具无参数，忽略）
    - ctx: 含db和current_user
    """
    # 获取用户画像
    profile = await profile_service.get_profile(ctx.db, ctx.current_user.id)

    if profile is None:
        return {
            "error": "该用户不存在"
        }

    # 将 ORM 对象转换成 JSON 可序列化的 dict
    # Decimal 要float() 才能JSON序列化
    return {
        "gender": profile.gender,
        "age": profile.age,
        "height_cm": profile.height_cm,
        "current_weight_kg": float(profile.current_weight_kg),
        "target_weight_kg": float(profile.target_weight_kg),
        "activity_level": profile.activity_level,
        "training_days_per_week": profile.training_days_per_week,
        "diet_preference": profile.diet_preference,
        "health_notes": profile.health_notes,
        "goal_description": profile.goal_description
    }

# 注册工具到全局
# description 很重要， LLM 通过description 决定是否调用这个工具，要写得具体、场景化
query_user_profile = Tool(
    name="query_user_profile",
    description="查询当前用户的健康画像（性别、年龄、身高、体重、活动水平、饮食偏好、健康备注等）。当需要给个性化健康建议时调用。",
    parameters={
        # OpenAI JSON Schema 格式： 这个工具无参数
        "type": "object",
        "properties": {},
        "required": [],
    },
    handler=_handler
)

register_tool(query_user_profile)
    