import asyncio
from app.agent.moonshot_client import chat_completion

async def main():
    messages = [
        {"role": "user",  "content": "你好，用一句话介绍你自己"}
    ]
    resp = await chat_completion(messages)
    print(resp)
    print("usages:", resp.get("usage"))


asyncio.run(main())