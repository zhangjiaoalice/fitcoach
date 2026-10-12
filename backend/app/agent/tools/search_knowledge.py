"""
工具： 在健身知识库中按语义检索相关段落
用户问： '卧推组数怎么安排/怎么突破减脂平台期/硬拉对腰椎的伤害' 等专业问题时调用。
"""
from typing import Any

from sqlalchemy import select

from app.agent.embedding_client import embed_one
from app.agent.tools.base import Tool, AgentContext, register_tool
from app.models.knowledge import Knowledge

# 单次返回的默认段数
DEFAULT_TOP_K = 3
# 单次返回的最大段数
MAX_TOP_K = 6
# 相似度阈值, 余𫠊值(cosine_distance)大于 0.6 的段不太相关，直接丢弃
MAX_DISTANCE = 0.6

async def _handler(arguments: dict, ctx: AgentContext) -> dict[str, Any]:
    """
    检索健身知识库中与用户问题相关的段落
    arguments 来自 LLM:
      query(str, 必填)： 用户问题的语义表达
      top_k(int, 可选)： 返回几段，默认3段
    """
    query: str = arguments["query"]
    top_k: int = min(arguments.get("top_k", DEFAULT_TOP_K), MAX_TOP_K)

    # 将query 转成向量， list[float] 1024 维
    query_vec = await embed_one(query)

    # pgvector 余𫠊距离检索 top_k
    stmt = (
        select(
            Knowledge,
            Knowledge.embedding.cosine_distance(query_vec).label("distance")
        )
        .order_by(Knowledge.embedding.cosine_distance(query_vec)) # 升序 = 相关性强的排在前面
        .limit(top_k)
    )

    results = await ctx.db.execute(stmt)
    rows = results.all() # 返回每一行的元组 [(Knowledge, distance), ...]

    # 组装返回， 按阈值过滤 + 字段裁剪
    hits: list[dict] = []
    for knowledge, distance in rows:
        if distance > MAX_DISTANCE:
            # 余𫠊值大于0.6，不太相关直接丢弃
            continue
        # 组装返回的内容
        hits.append({
            "title": knowledge.title,
            "source": knowledge.source,
            "content": knowledge.content,
            "similarity": round(1-distance, 3) # 将余𫠊值转成 “相似度”（0-1， 越接近1，越相关），语义检索的通用约定
        })

    if not hits:
        return {
            "count": 0,
            "hits": [],
            "message": "知识库中没有找到相关内容，请基于通用健身知识回答，并明确告知用户‘没有直接的知识库引用’"
        }

    return {
        "count": len(hits),
        "hits": hits,
        "message": "success"
    }

search_knowledge = Tool(
    name="search_knowledge",
    description=(
        "在健身知识库中按语意检索相关段落"
        "当用户问训练/营养/减脂/增肌等专业问题时调用。例如："
        "'卧推怎么安排训练组数''减脂平台期怎么办''硬拉会损伤腰椎吗''增肌期应该吃多少碳水''轻断食适合什么人群'。"
        "返回的hits里的字段都有 title, source, content, similarity,"
        "你回答时必须明确引用来源（如 '根据《strength_training.md》的 《我腿组数与次数的选择》段...'）"
        "如果 count=0， 就基于通用常识并告诉用户知识库没有直接内容。"
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "检索关键句，建议用问题的核心语义(如 '卧推组数怎么安选' '减脂平台期怎么办')",
            },
            "top_k": {
                "type": "integer",
                "description": "返回最相关的几段，默认3段，最多6段",
                "default": 3,
                "minimum": 1,
                "maximum": 6
            }
        },
        "required": ["query"]
    },
    handler=_handler
)

register_tool(search_knowledge)