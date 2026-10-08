import asyncio
import sys
from pathlib import Path

# 直接 `python ./tests/test_embed.py` 运行时，脚本目录(tests/)会被加入 sys.path，
# 但 `app` 包在项目根目录(backend/)。这里把项目根目录加进路径，确保 `from app...` 可导入。
# 用 pytest 运行时（pytest.ini 已配置 pythonpath=.）这一段不会造成任何副作用。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.embedding_client import embed_one, embed_batch

async def main():
    # 单条测试
    vec = await embed_one("卧推组数怎么安排")
    print(f"单条: 纬度={len(vec)}, 前 5 维={vec[:5]}")

    # 批量测试
    vecs = await embed_batch(["卧推 6 组 5-8 次是力量训练",
        "深蹲是下肢复合动作",
        "碳水应该占每日热量的 40-50%",])
    print(f"批量: 纬度={len(vecs)}, 每条维度={len(vecs[0])}")


    # 语意相似验证: 同类主题应该向量接近
    import math
    def cos_sim(a, b):
        dot = sum(x*y for x, y in zip(a, b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(x*x for x in b))
        return dot / (na * nb)

    v_press = await embed_one("卧推怎么练")
    v_squat = await embed_one("深蹲怎么练")
    v_carb = await embed_one("碳水应该吃多少")

    print(f"\n卧推 vs 深蹲(都是训练): {cos_sim(v_press, v_squat):.3f}")
    print(f"卧推 vs 碳水(训练 vs 饮食): {cos_sim(v_press, v_carb):.3f}")
    # 预期: 训练 vs 训练 > 训练 vs 饮食(数字越接近 1 越相似)

asyncio.run(main())