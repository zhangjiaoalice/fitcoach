import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.agent.tools.base import AgentContext, TOOL_REGISTRY
import app.agent.tools.query_user_profile


async def main():
    async with AsyncSessionLocal() as db:
        # 拿一个真实用户
        user = await db.get(User, 3)
        ctx = AgentContext(db, current_user=user)

        tool = TOOL_REGISTRY["query_user_profile"]
        result = await tool.run({}, ctx)
        print(result)

asyncio.run(main())