import asyncio
from app.agent.moonshot_client import chat_completion_stream

async def main():
    print("Kimi 开始回答：", flush=True)
    async for choice in chat_completion_stream(
        [{"role": "user", "content": "3句话介绍一下增肌的底层原理"}]
    ):
        delta = choice.get("delta", {}) or {}
        content = delta.get("content", "")
        if content:
            print(content, end="", flush=True)
    print()

asyncio.run(main())

