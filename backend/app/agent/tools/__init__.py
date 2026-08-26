"""
所有工具在这里import一遍，触发 register_tool
Loop 只要 import app.agent.tools 就能拿到所有工具
"""

from app.agent.tools import query_user_profile # noqa: F401
from app.agent.tools import query_diet_by_date # noqa: F401