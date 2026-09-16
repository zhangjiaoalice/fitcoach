"""
Agent Loop - 核心对话循环
心智模型：
  while 循环调 LLM ，直到LLM 不再要求调用工具，返回最终的文本
  每一轮： 把messages 传给 LLM -> 看 tool_calls
  如果 tool_calls 为空，则返回最终的文本
  如果 tool_calls 不为空，则调用工具，然后继续循环
"""

import json
from datetime import date
from typing import AsyncGenerator

import app.agent.tools

from app.agent.moonshot_client import chat_completion, chat_completion_stream
from app.agent.tools.base import AgentContext, TOOL_REGISTRY


def _build_system_prompt() -> str:
    """
    每次对话动态生成 system prompt。
    关键: 注入今天日期,否则 LLM 不知道 "今天" 是什么日期(它按训练截止日期猜)。
    """
    today = date.today().isoformat()
    weekday = ["一", "二", "三", "四", "五", "六", "日"][date.today().weekday()]
    return f"""你是 FitCoach 的健康教练助手。
今天是 {today}(星期{weekday})。当用户说"今天""昨天""上周"时,以此为准计算日期。

你可以调用工具查询用户画像和记录数据,也可以帮用户记录饮食/训练/体重。
- 用户询问个性化建议时,先调 query_user_profile 了解基本情况再回答
- 用户说"帮我记 XXX""我今天吃了 XXX"时,调 log_diet/log_workout/log_weight
- 记录时不要瞎编营养数据,用户没给的字段就让它空着

回答要具体、贴合用户的实际情况,不要给通用套话。"""


# 向后兼容: 旧代码里的 SYSTEM_PROMPT 常量仍可用(取当前时刻快照)
SYSTEM_PROMPT = _build_system_prompt()

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
        {"role": "system", "content": _build_system_prompt()},
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

async def run_agent_stream(
    user_message: str,
    ctx: AgentContext,
    max_iterations: int = 10
) -> AsyncGenerator[dict, None]:
    """
    流式调用版本, loop agent
    yield 出来的每一项是给路由用的事件dict:
    {"type": "delta", "content":"..."} # 文本片段
    {"type": "tool_start", "name": "...", "arguments": {...}} # 开始调用工具
    {"type": "tool_result", "name": "...", "result": "..."} # 工具调用结果
    {"type": "done", "reply": "...", "iterations": n, "tool_calls": [...]} # LLM 调用完成
    {"type": "error", "message": "..."} # 错误信息

    1. 拼content
    2. 拼 tool_calls
    3. 判断本轮结束： finish_reason
    4. 对外yield 事件： 每收到一段content 就yield 出去给路由，路由再通过SSE 推给前端
    5. 工具执行完后进入下一轮
    """

    messages: list[dict] = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": user_message}
    ]

    # 从 TOOL_REGISTRY 中获取所有的工具，并将所有工具转换成 openai JSON schema 格式
    tools = [t.to_openai_schema() for t in TOOL_REGISTRY.values()]

    # 记录工具调用的次数，方便debug和trace list[dict]
    tool_calls_records = []

    # 累计最终回复（用于done事件和后续写trace）
    final_reply = ""

    for i in range(max_iterations):
        # 累计assistant content
        content_buf = ""
        # index -> {id, name, argument_str}, index 对应工具 序号， 流式msg 每次至给一个小片，工具按index归组
        tool_calls_buf: dict[int, dict] = {}
        # 判断本轮是否结束
        finish_reason: str | None = None

        # 消费流式帧
        async for choice in chat_completion_stream(messages, tools):
            # 当前帧的增量文本/工具调用片段
            delta = choice.get("delta") or {} 
            # 拼content
            piece = delta.get("content")
            if piece:
                content_buf += piece
                # 每收到一段文本就吐给路由
                yield {"type": "delta", "content": piece}

            # 拼 tool_calls
            for tc_delta in delta.get("tool_calls") or []:
                # tool 片段按 index 归组
                idx = tc_delta["index"]
                # slot 是工具调用的片段，按 index 归组， 每次收到一个工具调用片段，就更新 slot
                # 如果 slot 不存在，则创建一个新的 slot，如果 slot 存在，则更新 slot
                # setdefault 方法表示：如果 key 不存在，则创建一个新的 value，如果 key 存在，则返回已有的 value
                slot = tool_calls_buf.setdefault(idx, {
                    "id": None,
                    "name": None,
                    "arguments": ""
                })

                # 为第一帧添加id和name
                if tc_delta.get("id"):
                    slot["id"] = tc_delta["id"]
                fn = tc_delta.get("function") or {}
                if fn.get("name"):
                    slot["name"] = fn["name"]
                if fn.get("arguments"):
                    slot["arguments"] += fn["arguments"]

            # 结束标志
            if choice.get("finish_reason"):
                finish_reason = choice["finish_reason"]

        # 本轮结束，开始下一步判断
        
        # 情况一: LLM 说完了 -> loop 收尾
        if finish_reason == "stop" or not tool_calls_buf:
            final_reply = content_buf
            yield {"type": "done", "reply": final_reply, "iterations": 1 + i, "tool_calls": tool_calls_records}
            return

        # 情况2: LLM 调用工具
        assistant_msg: dict = {"role": "assistant", "content": content_buf or None}
        # OpenAI/Moonshot 规范：tool_calls 每项必须是
        # {"id": "...", "type": "function", "function": {"name": "...", "arguments": "<json str>"}}
        # 少了 type/function 嵌套，服务端会报 "tokenization failed"
        assistant_msg["tool_calls"] = [
            {
                "id": slot["id"],
                "type": "function",
                "function": {
                    "name": slot["name"],
                    "arguments": slot["arguments"],  # 保持 JSON 字符串，不要 loads
                },
            }
            for slot in tool_calls_buf.values()
        ]
        messages.append(assistant_msg)

        # 逐个执行工具
        for slot in tool_calls_buf.values():
            fn_name = slot["name"]
            try:
                # json.loads =<json字符串> -> <dict>
                # json.dumps =<dict> -> <json字符串>
                arguments = json.loads(slot["arguments"])
            except json.JSONDecodeError:
                arguments = {}
            # 通知前端开始调用工具
            yield {"type": "tool_start", "name": fn_name, "arguments": arguments}

            tool = TOOL_REGISTRY.get(fn_name)
            if tool is None:
                result = {"error": f"工具 {fn_name} 不存在"}
            else:
                try:
                    result = await tool.run(arguments, ctx)
                except Exception as e:
                    result = {"error": f"工具{fn_name} 执行失败: {e}"}
            # 记录工具调用次数
            tool_calls_records.append({
                "name": fn_name,
                "arguments": arguments,
                "result": result
            })

            # 通知前端工具调用结果
            yield {"type": "tool_result", "name": fn_name, "result": result}

            # 把工具调用结果塞回 messages， 供下一轮llm 参考
            messages.append({
                "role": "tool",
                "tool_call_id": slot["id"],
                "content": json.dumps(result, ensure_ascii=False, default=str)
            })

    # 最大调用次数耗尽保护
    yield {"type": "error", "message": f"LLM 调用工具次数超过最大限制{max_iterations}"}
