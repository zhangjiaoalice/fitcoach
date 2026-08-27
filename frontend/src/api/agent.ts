/**
 * Agent 对话 API
 */
import { apiFetch } from "./client";
import type { ChatIn, ChatOut } from "./types";

export function chat(input: ChatIn): Promise<ChatOut> {
  return apiFetch<ChatOut>("/agent/chat", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
