"""
Moonshot / Kimi 客户端
封装对 /v1/chat/completions 接口的调用，把 message + tools 丢进去，拿回响应json
"""
import httpx
from app.core.config import get_settings

settings = get_settings()

async def chat_completion(messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.6) -> dict:
    """ 
    调 Moonshot 的对话接口
    参数：
        messages: [{"role": "system" / "user" / "tool" / "assistant", "content": ...}, ...]
        tools: 可选，工具定义列表（OpenAI 格式）
        temperature: 采样温度， 0～1， 越高越发散
    返回：
        Moonshot 响应 JSON(完整对象，含 choices/usage 等)
    """

    url = settings.moonshot_base_url + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.moonshot_api_key}",
        "Content-Type": "application/json"
    }

    # 构造请求体
    payload = {
        "model": settings.moonshot_model,
        "messages": messages,
        "temperature": temperature
    }

    # 工具
    if tools:
        payload["tools"] = tools

    # 发送请求
    # timeout: LLM 的调用可能很慢， httpx 默认5s，一超时就认为api挂了，给LLM 调用留够时间
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        # 检查响应 response.raise_for_status() 会在4xx/5xx 时抛出异常，方便排错
        response.raise_for_status()
        # 返回解析后的dict
        return response.json()