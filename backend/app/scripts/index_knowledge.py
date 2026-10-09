"""
将markdown 知识库建成向量索引

运行：
python -m app.scripts.index_knowledge knowledge_source/strength_training.md
python -m app.scripts.index_knowledge knowledge_source/*.md

设计：
- 按 "## 二级标题自然分片"
- 过长段(> 500 字) 按 300 字硬切， 带 50 字 overlap(保持上下文连贯)
- 冥等： 同 source 已有的旧行险删除再入
- 批量 embed 25 条 / 次（智谱 API 上限）
"""
import asyncio
# re 处理正则表达式
# import re
import sys
from pathlib import Path

from sqlalchemy import delete

from app.agent.embedding_client import embed_batch
from app.db.session import AsyncSessionLocal
from app.models.knowledge import Knowledge

# 调参点
CHUNK_MAX_CHARS = 500 # 单段最大字符数，超过就硬切
HARD_CHUNK_SIZE = 300 # 硬切目标大小
HARD_CHUNK_OVERLAP = 50 # 硬切overlap（前后段共享 50 字，减少语义断裂）
EMBED_BATCH_SIZE = 20 # embed 批量大小（智谱上限25， 留点余量）

def parse_markdown(text: str) -> list[dict]:
    """
    将markdown 按 二级标题 ## 切成段
    返回：[{"title": "卧推组数...", "content": "..."}, ...]
    """
    sections: list[dict] = [] # 切分的片段
    current_title = None # 记录当前的标题
    current_lines = [] # 记录当前扫描的行的内容, 目的是将多行合并为一个段落

    # 逐行扫描，遇到 “## ” 就切为新的一段
    for line in text.split('\n'):
        if line.startswith('## '):
            if current_title:
                # 存在上一段，将上一段添加到片段列表中
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_lines).strip()
                })
            current_title = line[3:].strip()
            current_lines = [] # 清空当前段
        elif current_title is not None:
            # 不是新的标题，继续添加到当前段
            current_lines.append(line)

    # 将最后一段添加到section中
    if current_title:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_lines).strip()
        })
    return sections

def chunk_long_sections(section: dict) -> list[dict]:
    """
    如果段落过长（> CHUNK_MAX_CHARS）,硬切成多片，带overlap
    每个切片共享title， 只切content
    section: {"title": "卧推组数...", "content": "..."}
    返回: [{"title": "卧推组数...", "content": "..."}, ...]
    """
    content = section["content"]
    if len(content) <= CHUNK_MAX_CHARS:
        return [section]
    chunks: list[dict] = []

    step = HARD_CHUNK_SIZE - HARD_CHUNK_OVERLAP # 每次切片的步长（300-50=250）
    for i in range(0, len(content), step):
        # 切片步长：i=0, i=250, i=500,...
        piece = content[i:i+HARD_CHUNK_SIZE] # [0:300], [250: 550], [500:800]
        if piece.strip():
            chunks.append({
                "title": section["title"],
                "content": piece.strip()
            })
    return chunks

async def index_file(file_path: Path) -> int:
    """
    索引一个 md 文件，返回写入的段数
    file_path: Path -> md 文件路径
    return: int -> 写入的段数
    """
    source = file_path.name # 文件名 + 后缀，如“strength_training.md”
    text = file_path.read_text(encoding="utf-8") # 读取文件内容

    # 将读取的文件内容进行切片
    sections = parse_markdown(text)
    chunks = [] # [{"title": "卧推组数...", "content": "..."}]
    for section in sections:
        # 将所有切片平铺添加到 chunks 列表中
        chunks.extend(chunk_long_sections(section))

    if not chunks:
        print(f"[warn] {source} 没有可索引的段落")
        return 0


    # 向量化 + 入库
    async with AsyncSessionLocal() as db:
        # 冥等： 先删除同source 的旧行（重跑脚本时不会推重复的数据）
        await db.execute(delete(Knowledge).where(Knowledge.source == source))
        await db.commit()

        for i in range(0, len(chunks), EMBED_BATCH_SIZE):
            # 步长 i=0, i=20, i=40...
            batch = chunks[i:i+EMBED_BATCH_SIZE] # [0:20], [20:40], [40:60]...
            texts = [c["content"] for c in batch]

            print(f"embed batch {i // EMBED_BATCH_SIZE + 1} ({len(batch)} 条)...")
            vectors = await embed_batch(texts)

            rows = []
            # 构造 Knowledge 对象批量入库， zip 将多个可迭代对象 按位置一一配对，打包成一个个元组
            # zip(batch, vectors) -> [(chunk1, vec1), (chunk2, vec2), ...]
            for chunk, vec in zip(batch, vectors):
                rows.append(Knowledge(
                    title=chunk["title"],
                    source=source,
                    content=chunk["content"],
                    embedding=vec,
                    token_count=len(chunk["content"]) # 粗略估算，中文字～1 token
                ))
            db.add_all(rows)
            await db.commit()

    return len(chunks)

async def main(paths: list[str]):
    total = 0
    for p in paths:
        file_path = Path(p)
        if not file_path.exists():
            print(f"[error] 文件不存在{p}")
            continue
        count = await index_file(file_path)
        total += count
    print(f"\n ✅索引完成，共 {total}段入库")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法： python -m app.scripts.index_knowledge <md文件...>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1:]))
