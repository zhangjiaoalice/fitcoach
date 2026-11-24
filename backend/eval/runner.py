"""
Agent 评估runner：

用法：
    cd backend
    .venv/bin/python -m eval.runner

产出：
    eval/reports/latest.json 机器可读
    eval/reports/latest.md 人类可读性
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

import yaml
from app.agent.loop import run_agent, _detect_crisis
from app.db.session import async_session_maker
from app.models.user import User
from sqlalchemy import select
from app.agent.tools.base import AgentContext

ROOT = Path(__file__).parent
CASES_FILE = ROOT / "cases.yaml"
REPORT_JSON = ROOT / "reports" / "latest.json"
REPORT_MD = ROOT / "reports" / "latest.md"

# 加载 golden set
def load_cases() -> list[dict]:
    # 读 cases.yaml, 返回 cases 列表
    with open(CASES_FILE, "r") as f:
        return yaml.safe_load(f)["cases"]

# 跑单条case，返回评估结果
async def run_one_case(case: dict, test_user: User, db) -> dict:
    """
    返回格式:
    {
    "id": "tool_diet_01",
    "input": "...",
    "category": "tool_call",
    "passed": True/False,
    "reason": [...], # 失败原因列表
    "actual_tool_calls": [...], # 实际调用的工具列表
    "actual_reply": "..."
    }
    """

    input_text = case["input"] # 用户输入query
    expect = case["expect"] # 期望结果（调用的工具和参数）

    # 先过 crisis 检测，检查是否命中危险关键词
    is_crisis = _detect_crisis(input_text)
    if expect.get("is_crisis") == True:
        return {
            "id": case["id"],
            "category": case.get("category", "safety"),
            "input": input_text,
            "passed": is_crisis,
            "reasons": [] if is_crisis else ["期望触发危机拦截但未命中"],
            "actual_tool_calls": [],
            "actual_reply": "(crisis flow, 未调LLM)"
        }

    # 构造 AgentContext 调 run_agent
    ctx = AgentContext(
        db=db,
        current_user=test_user
    )

    # result = {"reply": "...", "iteration": 2, "tool_calls": [{"name": "log_diet", "arguments": {...}}], "error": None}
    result = await run_agent(input_text, ctx, max_iterations=5)

    # 根据except 逐条校验，收集失败原因
    reasons: list[str] = []
    tool_calls = result.get("tool_calls", [])
    reply = result.get("reply", "")

    # 检查tool_name
    if "tool_name" in expect:
        excepted_tool = expect["tool_name"] # 期望调用的工具
        called_tools = [tc["name"] for tc in tool_calls] # 被调用的工具
        if excepted_tool not in called_tools:
            reasons.append(f"期望调用 {excepted_tool}, 实际调用 {called_tools or '无'}")


    # 检查tool_name_should_be_one_of
    if "tool_name_should_be_one_of" in expect:
        allowed = expect["tool_name_should_be_one_of"]
        called_tools = [tc["name"] for tc in tool_calls]
        if not any(t in called_tools for t in allowed):
            reasons.append(f"期望调用 {allowed} 之一，实际调用 {called_tools or '无'}")

    # 检查 tool_args_subset(期望字段是实际字段的子集)
    if "tool_args_subset" in expect and tool_calls:
        excepted_args = expect["tool_args_subset"]
        matched = False
        for tc in tool_calls:
            actual_args = tc.get("arguments", {})
            if all(actual_args.get(k) == v for k, v in excepted_args.items() if not k.endswith("_contains")):
                # 处理_contains 的子串匹配
                matched = True
                break
        if not matched:
            reasons.append(f"参数不符： 期望{excepted_args}, 实际{[tc.get('arguments') for tc in tool_calls]}")

    # 检查 replay_should_contain（必须要包含的关键字）
    if "reply_should_contain" in expect:
        for word in expect["reply_should_contain"]:
            if word not in reply:
                reasons.append(f"reply 缺少关键字`{word}`")

    # 检查 reply_should_contain_any（至少包含一个候选关键字）
    if "reply_should_contain_any" in expect:
        if not any(word in reply for word in expect["reply_should_contain_any"]):
            reasons.append(f"reply 未命中任一候选关键字 {expect['reply_should_contain_any']}")

    # 检查 reply_should_not_contain
    if "reply_should_not_contain" in expect:
        for word in expect["reply_should_not_contain"]:
            if word in reply:
                reasons.append(f"reply 不该出现 `{word}`,，但出现了")

    # 检查 rag_topic_keywords(遍历 search_knowledge 的工具返回，看返回的content 是否包含关键字)
    if "rag_topic_keywords" in expect:
        rag_hits = []
        for tc in tool_calls:
            if tc.get("name") == "search_knowledge":
                # result 可能是 dict / list / str,看实际的返回
                result_str = json.dumps(tc.get("result", ""), ensure_ascii=False)
                rag_hits.append(result_str)
            
        rag_all_content = " ".join(rag_hits) + " " + reply # 工具结果 + reply 双重命中
        for keyword in expect["rag_topic_keywords"]:
            if keyword not in rag_all_content:
                reasons.append(f"RAG 未命中关键词 `{keyword}`")
    # 需要在 run_agent 返回里带上tool_results, 或者在tool_calls 里能看到 result

    return {
        "id": case["id"],
        "category": case.get("category", "unknown"),
        "input": input_text,
        "passed": len(reasons) == 0,
        "reasons": reasons,
        "actual_tool_calls": tool_calls,
        "actual_reply": reply[:200] # 截断，不要太长
    }


            
# 主流程
async def main() -> None:
    cases = load_cases()
    print(f"📃 加载 {len(cases)} 条case")

    # 建db session, 拿一个测试用
    async with async_session_maker() as db:
        # 拿 user_id = 1 或任何已知用户测试
        user = (await db.execute(select(User).limit(1))).scalar_one()

        results = []

        for i, case in enumerate(cases, 1):
            print(f" [{i}/{len(cases)}] {case['id']} ...", end=" ", flush=True)
            try:
                r = await run_one_case(case, user, db)
                print("✅" if r["passed"] else "❌")
                results.append(r)

            except Exception as e:
                print(f"🔥 {e}")
                results.append({
                    "id": case["id"],
                    "passed": False,
                    "reasons": [f"RUNTIME ERROR: {e}"],
                    "category": case.get("category", "unknown")
                })

    # 汇总统计
    summary = compute_summary(results)
    print(f"\n {'='*50}")
    print(f"总体通过率： {summary['overall_pass_rate']:.0%}")
    for cat, stat in summary["by_category"].items():
        print(f" {cat:15s}: {stat['passed']}/{stat['total']} ({stat['pass_rate']:.0%})")


    # 写JSON + MD 报告
    write_reports(results, summary)
    print(f"\n 📝 报告已写入 {REPORT_JSON}")


def compute_summary(results: list[dict]) -> dict:
    """汇总统计:
    按 category 统计 passed / total / pass_rate
    """
    by_category: dict[str, dict] = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = {"passed": 0, "total": 0, "pass_rate": 0.0}
        by_category[cat]["total"] += 1
        if r["passed"]:
            by_category[cat]["passed"] += 1

    # 算每个category的pass_rate
    for stat in by_category.values():
        stat["pass_rate"] = stat["passed"] / stat["total"] if stat["total"] else 0

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "overall_pass_rate": passed / total if total else 0,
        "by_category": by_category
    }



def write_reports(results: list[dict], summary: dict) -> None:
    """写 JSON报告 + MD 报告"""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    # JSON
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "results": results
    }

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # Markdown
    md_lines: list[str] = [
        f"# FitCoach 评估报告",
        f"",
        f"生成时间：{report['generated_at']}",
        f"",
        f"## 总体",
        f"- 通过率: **{summary['passed']}/{summary['total']} ({summary['overall_pass_rate']:.0%})**",
        f"- 失败: {summary['failed']}",
        f"",
        f"## 分类明细",
        f"",
        f"| 类别 | 通过 | 总数 | 通过率 |",
        f"|---|---|---|---|",
    ]

    for cat, stat in summary["by_category"].items():
        md_lines.append(f"| {cat} | {stat['passed']} | {stat['total']} | {stat['pass_rate']:.0%} |")

    # 失败详情
    failed = [r for r in results if not r['passed']]
    if failed:
        md_lines.extend(["", "## 失败 case 详情", ""])
        for r in failed:
            md_lines.extend([
                f"### ❌ {r['id']} ({r.get('category', '?')})",
                f"",
                f"- 输入: `{r.get('input', '')}`",
                f"- 失败原因:"
            ])

            for reason in r.get("reasons", []):
                md_lines.append(f"  - {reason}")
            if r.get('actual_tool_calls'):
                tool_names = [tc.get("name") for tc in r['actual_tool_calls']]
                md_lines.append(f"- 实际工具调用: {tool_names}")
            if r.get('actual_reply'):
                md_lines.append(f"- 实际回复：`{r['actual_reply']}`")
            md_lines.append("")

    REPORT_MD.write_text(
        "\n".join(md_lines),
        encoding="utf-8"
    )

if __name__ == "__main__":
    asyncio.run(main())