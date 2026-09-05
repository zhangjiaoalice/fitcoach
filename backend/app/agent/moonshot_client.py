"""
Moonshot / Kimi 客户端
封装对 /v1/chat/completions 接口的调用，把 message + tools 丢进去，拿回响应json
"""
import httpx
from app.core.config import get_settings

settings = get_settings()

async def chat_completion(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """ 
    调 Moonshot 的对话接口
    参数：
        messages: [{"role": "system" / "user" / "tool" / "assistant", "content": ...}, ...]
        tools: 可选，工具定义列表（OpenAI 格式）
    返回：
        Moonshot 响应 JSON(完整对象，含 choices/usage 等)

    注：kimi-k3 等 reasoning 模型不接受自定义 temperature（只允许 1.0），
        所以这里不传 temperature，让服务端用默认值。
    """

    url = settings.moonshot_base_url + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.moonshot_api_key}",
        "Content-Type": "application/json"
    }

    # 构造请求体（kimi-k3 不允许自定义 temperature）
    payload = {
        "model": settings.moonshot_model,
        "messages": messages,
    }

    # 工具
    if tools:
        payload["tools"] = tools

    # 发送请求
    # timeout: LLM 的调用可能很慢， httpx 默认5s，一超时就认为api挂了，给LLM 调用留够时间
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        # 4xx/5xx 时先把 Moonshot 的错误 body 完整打出来（临时调试用，跑通后删除）
        if response.status_code >= 400:
            print(f"[Moonshot {response.status_code}] {response.text}")
            print(f"[Moonshot 发送的 payload keys] {list(payload.keys())}")
            print(f"[Moonshot model] {payload.get('model')}")
        # 检查响应 response.raise_for_status() 会在4xx/5xx 时抛出异常，方便排错
        response.raise_for_status()
        # 返回解析后的dict
        return response.json()