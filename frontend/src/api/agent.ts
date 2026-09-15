/**
 * Agent 对话 API。
 * chat        - 非流式(M4 版,一次拿完整回复)
 * chatStream  - 流式 SSE(M7 版,边收边渲染,推荐)
 */
import { ApiError, getToken } from "./client";
import type { AgentStreamEvent, ChatIn, ChatOut } from "./types";

// ─────────────────────────────────────────────
// 非流式(保留,方便对比)
// ─────────────────────────────────────────────
export function chat(input: ChatIn): Promise<ChatOut> {
  return fetch("/api/agent/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken() ?? ""}`,
    },
    body: JSON.stringify(input),
  }).then(async (r) => {
    if (!r.ok) throw new ApiError(r.status, await r.text());
    return r.json();
  });
}

// ─────────────────────────────────────────────
// 流式(SSE)
// ─────────────────────────────────────────────
export interface ChatStreamOptions {
  message: string;
  onEvent: (event: AgentStreamEvent) => void;
  signal?: AbortSignal; // 允许调用方中途取消
}

/**
 * 流式对话 —— 用 fetch + ReadableStream 消费后端 SSE。
 *
 * 为什么不用浏览器原生 EventSource:
 *   1. EventSource 只支持 GET(我们要 POST message)
 *   2. EventSource 不能加自定义 header(我们要 Bearer token)
 *
 * 关键陷阱:
 *   - 一次 read() 可能读到半条 SSE 帧,必须 buffer 累加
 *   - TextDecoder 加 { stream: true } 保留跨 chunk 的多字节字符
 *   - 每条 SSE 帧以 \n\n 结尾,按它 split
 */
export async function chatStream(opts: ChatStreamOptions): Promise<void> {
  const token = getToken();
  if (!token) throw new ApiError(401, "未登录");

  const response = await fetch("/api/agent/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ message: opts.message }),
    signal: opts.signal,
  });

  if (!response.ok) {
    // 非 2xx 尝试解析错误详情
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* 忽略 */
    }
    throw new ApiError(response.status, detail);
  }

  if (!response.body) {
    throw new ApiError(500, "SSE 响应无 body,浏览器不支持流式读取");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      // stream: true 保留多字节字符(中文一个字 3 字节,可能跨 chunk)
      buffer += decoder.decode(value, { stream: true });

      // 按 \n\n 切出完整帧,最后一段(可能不完整)留在 buffer
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        // 一帧可能有多行(如 event: xxx / data: yyy),我们只用 data: 那行
        const line = frame.split("\n").find((l) => l.startsWith("data: "));
        if (!line) continue;

        const payload = line.slice("data: ".length);
        if (payload === "[DONE]") return; // 兼容 OpenAI 风格结束标记

        try {
          const event = JSON.parse(payload) as AgentStreamEvent;
          opts.onEvent(event);
        } catch (e) {
          console.warn("[SSE] 帧 JSON 解析失败:", payload, e);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
