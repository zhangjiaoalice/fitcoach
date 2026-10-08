"""
智谱 Embedding 客户端
把文本专程 1024 维向量，给RAG 用
设计：
- 支持单条（embed_one）和 批量（embed_batch）
- 复用 moonshot 的 http.AsyncClient 模式
"""
import httpx
from app.core.config import get_settings

settings = get_settings()

EMBEDDING_DIM = 1024 # 智谱 Embedding 维度

async def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    批量把文本 -> 向量列表
    每次最多传 25条（智谱单请求上限），索引大量文档时调用方要自己分批
    参数：
        texts: 待向量化的文本列表，如：["卧推怎么练", "深蹲怎么练"]
    返回:
        向量列表，长度和 texts 文本的长度一样，每个是1024 维 float list
    """
    if not texts:
        return []

    # 校验 API Key，避免拼出非法请求头 "Bearer " 导致晦涩的 httpx.LocalProtocolError
    if not settings.zhipu_api_key:
        raise RuntimeError(
            "缺少智谱 API Key：请在 backend/.env 中设置 ZHIPU_API_KEY=你的key"
        )

    # 拼URL
    url = f"{settings.zhipu_base_url}/embeddings"

    headers = {
        "Authorization": f"Bearer {settings.zhipu_api_key}",
        "Content-Type": "application/json",
    }

    # 构造请求体
    payload = {
        "model": settings.zhipu_embedding_model,
        "input": texts,
        "dimensions": EMBEDDING_DIM,
    }

    # 发送请求 + 获取结果
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            print(f"[Zhipu {response.status_code}] {response.text}")
        response.raise_for_status() # 抛出异常，让调用方处理
        data = response.json()

        # 智谱返回的data 是 [{index, embedding}, {...}], 按index 排序确保对齐
        items = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in items]

async def embed_one(text: str) -> list[float]:
    """
    单条文本 -> 向量。用户提问检索时用这个，一次一个
    """

    vectors = await embed_batch([text])
    return vectors[0]