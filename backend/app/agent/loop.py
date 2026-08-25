"""
Agent Loop - 核心对话循环
心智模型：
  while 循环调 LLM ，直到LLM 不再要求调用工具，返回最终的文本
  每一轮： 把messages 传给 LLM -> 看 tool_calls
  如果 tool_calls 为空，则返回最终的文本
  如果 tool_calls 不为空，则调用工具，然后继续循环
"""

import json

import app.agent.tools

from app.agent.moonshot_client import chat_completion
from app.agent.tools.base import AgentContext, TOOL_REGISTRY

SYSTEM_PROMPT = """你是 FitCoach 的健康教练助手。
你可以调用工具查询用户的画像和记录数据。
当用户询问个性化建议时，先调 query_user_profile 了解基本情况再回答。
回答要具体、贴合用户的实际情况，不要给通用套话。"""

async def run_agent(
        user_message: str,
        ctx: AgentContext,
        max_iterations: int = 10
) -> dict:
    """
    完整跑一轮Agent 对话
    返回：
    {
        "reply": 最终回复文本
        "iterations": 迭代次数
        "tool_calls": [{"name": "", "arguments": {}, "result": "..."}, {...}, ...]
    }
    """

    # 构造messages 存放对话历史
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # 从 TOOL_REGISTRY 中获取所有的工具，并将所有工具转换成 openai JSON schema 格式
    tools = [t.to_openai_schema() for t in TOOL_REGISTRY.values()]

    # 记录工具调用的次数，方便debug和trace list[dict]
    tool_calls_records = []  

    for i in range(max_iterations):
        # 调用 LLM
        resp = await chat_completion(messages, tools)
        msg = resp["choices"][0]["message"]

        tool_calls = msg.get("tool_calls")

        if not tool_calls:
            """LLM 没要求调用工具-循环结束，返回最终的结果"""
            return {
                "reply": msg.get("content", ""),
                "iterations":  i + 1,
                "tool_calls": tool_calls_records
            }

        # 将 LLM assistant 消息塞回messages
        messages.append(msg)

        # 执行 LLM 要求的工具
        for call in tool_calls:
            fn_name = call["function"]["name"]
            # LLM 给 arguments 是 JSON 字符串，需要解析成字典 json -> dict: json.loads()
            arguments = json.loads(call["function"]["arguments"])

            tool = TOOL_REGISTRY.get(fn_name)
            if tool is None:
                result = {"error": f"工具 {fn_name} 不存在"}
            else:
                try:
                    result = await tool.run(arguments, ctx)
                except Exception as e:
                    result = {"error": f"工具 {fn_name} 执行失败: {e}"}
            # 记录工具调用
            tool_calls_records.append({
                "name": fn_name,
                "arguments": arguments,
                "result": result
            })
            # 将工具执行结果塞回 messages
            messages.append({
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False, default=str),
                "tool_call_id": call["id"],
            })

    # 循环耗尽保护 - LLM 可能一直要求调用工具
    raise RuntimeError(f"LLM 调用工具次数超过最大限制{max_iterations}")

