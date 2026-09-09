"""脱离http,单独测loop"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.agent.tools.base import AgentContext
from app.agent.loop import run_agent

async def main():
    async with AsyncSessionLocal() as db:
        user = await db.get(User, 3)
        ctx = AgentContext(db=db, current_user=user)

        # 这句会触发 LLM 决定调query_user_profile
        result = await run_agent("根据我的画像给我推荐一份午餐", ctx)

        print("回复：", result["reply"])
        print("轮数：", result["iterations"])
        print("工具调用历史：", result["tool_calls"])

asyncio.run(main())