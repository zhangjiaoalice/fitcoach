<script setup lang="ts">
import { nextTick, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import Icon from "../components/Icon.vue";
import { chat } from "../api/agent";
import { ApiError } from "../api/client";
import type { AgentToolCall } from "../api/types";

const router = useRouter();

function goBack(): void {
  if (window.history.length > 1) router.back();
  else router.push({ name: "dashboard" });
}

/**
 * 对话消息 —— 三种类型：
 *   - user      用户气泡
 *   - assistant AI 气泡（可能带工具调用记录）
 *   - error     错误提示
 */
interface UserMessage {
  id: number;
  type: "user";
  text: string;
}

interface AssistantMessage {
  id: number;
  type: "assistant";
  text: string;
  toolCalls: AgentToolCall[];
  iterations: number;
}

interface ErrorMessage {
  id: number;
  type: "error";
  text: string;
}

type ChatMessage = UserMessage | AssistantMessage | ErrorMessage;

const messages = ref<ChatMessage[]>([
  {
    id: 0,
    type: "assistant",
    text: "你好，我是你的 FitCoach AI 教练。可以问我：\n\n· 我的画像是什么？\n· 帮我推荐一份适合减脂的午餐\n· 我最近一周体重变化怎样？",
    toolCalls: [],
    iterations: 0,
  },
]);

const inputText = ref("");
const sending = ref(false);
const scrollRef = ref<HTMLElement | null>(null);

let nextId = 1;

function pushMessage(msg: ChatMessage): void {
  messages.value.push(msg);
  void nextTick(scrollToBottom);
}

function scrollToBottom(): void {
  const el = scrollRef.value;
  if (el) el.scrollTop = el.scrollHeight;
}

async function handleSend(): Promise<void> {
  const text = inputText.value.trim();
  if (!text || sending.value) return;

  // 1. 先把用户消息落到视图
  pushMessage({ id: nextId++, type: "user", text });
  inputText.value = "";
  sending.value = true;

  try {
    // 2. 调后端 Agent Loop
    const resp = await chat({ message: text });
    // 3. 落 AI 消息（包含工具调用轨迹）
    pushMessage({
      id: nextId++,
      type: "assistant",
      text: resp.reply,
      toolCalls: resp.tool_calls,
      iterations: resp.iterations,
    });
  } catch (err) {
    const detail = err instanceof ApiError ? err.message : "网络异常，请稍后再试";
    pushMessage({ id: nextId++, type: "error", text: detail });
  } finally {
    sending.value = false;
  }
}

function toolIcon(name: string): string {
  if (name.includes("profile")) return "user";
  if (name.includes("diet")) return "fork";
  if (name.includes("workout")) return "flame";
  if (name.includes("weight")) return "scale";
  return "spinner";
}

function toolLabel(name: string): string {
  const map: Record<string, string> = {
    query_user_profile: "查询用户画像",
    query_diet_by_date: "查询饮食记录",
    query_workout_by_date: "查询训练记录",
    query_weight_trend: "查询体重趋势",
  };
  return map[name] ?? name;
}

onMounted(scrollToBottom);
</script>

<template>
  <div class="chat-page">
    <header class="hd">
      <button class="back" @click="goBack" aria-label="返回">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>
      <div class="title">
        <h1>AI 教练</h1>
        <p>Kimi 驱动 · 可查画像 / 饮食 / 训练 / 体重</p>
      </div>
      <div class="av">FC</div>
    </header>

    <div ref="scrollRef" class="msgs">
      <template v-for="m in messages" :key="m.id">
        <!-- 用户气泡 -->
        <div v-if="m.type === 'user'" class="bub bu">{{ m.text }}</div>

        <!-- AI 气泡（前面铺工具调用卡片） -->
        <template v-else-if="m.type === 'assistant'">
          <div v-for="(tc, ti) in m.toolCalls" :key="`${m.id}-tc-${ti}`" class="tool glass">
            <span class="ic brand">
              <Icon :name="toolIcon(tc.name)" :size="14" color="var(--brand)" :width="2.2" />
            </span>
            <span>{{ toolLabel(tc.name) }}</span>
            <span class="st">完成</span>
          </div>
          <div class="bub ba">{{ m.text }}</div>
        </template>

        <!-- 错误提示 -->
        <div v-else class="tool risk">
          <span class="ic warn"><Icon name="warn" :size="14" color="var(--warn)" :width="2.2" /></span>
          <span style="color: var(--warn)">{{ m.text }}</span>
        </div>
      </template>

      <!-- 正在生成 -->
      <div v-if="sending" class="typing">
        <span class="dot" />
        <span class="dot" />
        <span class="dot" />
      </div>
    </div>

    <form class="composer" @submit.prevent="handleSend">
      <input
        v-model="inputText"
        type="text"
        placeholder="问点什么，比如'我今天该吃啥？'"
        :disabled="sending"
        autofocus
      />
      <button type="submit" :disabled="sending || !inputText.trim()">
        <Icon name="check" :size="18" color="var(--on-brand)" :width="2.4" />
      </button>
    </form>
  </div>
</template>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  /* 减去 PhoneShell 的 notch 28 */
  min-height: calc(100vh - 28px);
  padding-bottom: 64px; /* 输入框高度 + 一点余量 */
}

.hd {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 0 14px;
}
.back {
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 0;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-1);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.back:hover { background: rgba(255, 255, 255, 0.09); }
.title { flex: 1; }
.title h1 { font-size: 18px; font-weight: 500; letter-spacing: -0.02em; }
.title p { font-size: 11px; color: var(--text-3); margin-top: 2px; }
.av {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--brand-grad); color: var(--on-brand);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 500;
  flex-shrink: 0;
}

.msgs {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
  -webkit-overflow-scrolling: touch;
}

.bub {
  max-width: 82%;
  padding: 11px 14px;
  font-size: 13px;
  line-height: 1.55;
  margin-bottom: 10px;
  border-radius: 16px;
  white-space: pre-wrap;
  word-break: break-word;
}
.bu {
  background: var(--brand-grad);
  color: var(--on-brand);
  margin-left: auto;
  border-bottom-right-radius: 5px;
}
.ba {
  color: var(--text-2);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--hairline);
  border-bottom-left-radius: 5px;
}

.tool {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-2);
  border-radius: 12px;
}
.tool .ic {
  width: 26px; height: 26px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ic.brand { background: rgba(16, 185, 129, 0.14); }
.ic.warn { background: rgba(234, 179, 8, 0.18); }
.tool .st { margin-left: auto; font-size: 11px; color: var(--brand-bright); }
.risk { background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.25); }

/* 三点打字动画 */
.typing {
  display: inline-flex;
  gap: 4px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--hairline);
  border-radius: 16px;
  border-bottom-left-radius: 5px;
  margin-bottom: 10px;
}
.typing .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--text-3);
  animation: bounce 1.2s infinite ease-in-out;
}
.typing .dot:nth-child(2) { animation-delay: 0.15s; }
.typing .dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* 输入框 —— fixed 定位，贴屏幕底部，不跟随滚动 */
.composer {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 12px;
  width: 100%;
  max-width: 384px; /* PhoneShell 内宽 = 420 - 左右 padding 18*2 */
  box-sizing: border-box;
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(20, 25, 33, 0.92);
  backdrop-filter: blur(10px);
  border: 1px solid var(--hairline);
  border-radius: 999px;
  z-index: 20;
}
.composer input {
  flex: 1;
  padding: 10px 14px;
  border: 0;
  background: transparent;
  color: var(--text-1);
  font-size: 13px;
  outline: none;
}
.composer input::placeholder { color: var(--text-4); }
.composer button {
  width: 38px; height: 38px;
  border-radius: 50%;
  border: 0;
  background: var(--brand-grad);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.composer button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
