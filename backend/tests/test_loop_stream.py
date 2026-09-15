import asyncio

from app.agent.tools.base import AgentContext
from app.agent.loop import run_agent_stream
from app.models.user import User
from app.db.session import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as db:
        user = await db.get(User, 3)
        ctx = AgentContext(db = db, current_user = user)
        async for event in  run_agent_stream("根据我的画像给我推荐一份午餐", ctx):
            t = event["type"]
            if t == "delta":
                print(event["content"], end="", flush=True) # 边打印边接收
            elif t == "tool_start":
                print(f"\n[TOOL START] {event['name']}({event['arguments']})", flush=True)
            elif t == "tool_result":
                print(f"\n[TOOL RESULT] {event['name']} → keys={list(event['result'].keys())}", flush=True)
            elif t == 'done':
                print(f"\n[DONE] iterations={event['iterations']}", flush=True)
            elif t == 'error':
                print(f"\n[ERROR] {event['message']}", flush=True)


asyncio.run(main())