<script setup lang="ts">
/**
 * 记录 Tab 聚合页
 *   - 展示 5 个记录入口 item：饮食/训练/饮水/体重/睡眠
 *   - 点击 item 跳转到具体记录子页（暂未实现，先 toast 占位）
 *   - 卡通可爱风，和 Dashboard / Onboarding 一致
 */
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import Mascot from "../components/Mascot.vue";
import { getRecordSummary, RecordSummary } from "../api/record";

const router = useRouter();

// 当前日期
const today = computed(() => {
  const d = new Date();
  return `${d.getMonth() + 1} 月 ${d.getDate()} 日`;
});

const summary = ref<RecordSummary | null>(null);

interface RecordItem {
  key: "diet" | "workout" | "water" | "weight" | "sleep";
  emoji: string;
  label: string;
  sub: string;
  color: string; // 图标盒子底色
  accent: string; // 图标盒子描边 / 文字强调色
  routeName?: string; // 对应子页路由名（若未实现则为空）
  summary?: string; // 今日摘要
}

const items: RecordItem[] = [
  {
    key: "diet",
    emoji: "🍱",
    label: "饮食",
    sub: "记录三餐和加餐",
    color: "#FFE5CF",
    accent: "#FF9F6B",
    summary: summary.value?.diet
      ? `今日 ${summary.value.diet.kcal} 千卡`
      : "去记录",
  },
  {
    key: "workout",
    emoji: "🏋️",
    label: "训练",
    sub: "力量 / 有氧 / 拉伸",
    color: "#DBEAFE",
    accent: "#3B82F6",
    summary: summary.value?.workout
      ? `今日 ${summary.value.workout.done} / ${summary.value.workout.total} 完成`
      : "去记录",
  },
  {
    key: "water",
    emoji: "💧",
    label: "饮水",
    sub: "喝水量追踪",
    color: "#CCFBF1",
    accent: "#14B8A6",
    summary: summary.value?.water
      ? `今日 ${summary.value.water.ml} / ${summary.value.water.target_ml} 毫升`
      : "去记录",
  },
  {
    key: "weight",
    emoji: "⚖️",
    label: "体重",
    sub: "每日称重记录",
    color: "#FEE2E2",
    accent: "#EF4444",
    summary: summary.value?.weight
      ? `今日 ${summary.value.weight.latest_weight}kg`
      : "去记录",
  },
  {
    key: "sleep",
    emoji: "🌙",
    label: "睡眠",
    sub: "入睡 / 睡眠时长",
    color: "#EDE9FE",
    accent: "#8B5CF6",
    summary: summary.value?.sleep
      ? `今日 ${summary.value.sleep.duration_min} 小时`
      : "去记录",
  },
];

onMounted(async () => {
  await getRecord();
});

// toast 轻提示
const toastMsg = ref("");
let toastTimer: ReturnType<typeof setTimeout> | null = null;
function showToast(msg: string): void {
  toastMsg.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMsg.value = "";
  }, 1800);
}

function openRecord(item: RecordItem): void {
  if (item.routeName) {
    router.push({ name: item.routeName });
  } else {
    // 子页还没想好，先 toast 占位
    showToast(`${item.label}记录页正在设计中 🛠️`);
  }
}

function goChat(): void {
  router.push({ name: "chat" });
}

async function getRecord() {
  const res = await getRecordSummary();
  console.log("获取记录：", res);
  summary.value = { ...res };
}
</script>

<template>
  <div class="rec">
    <!-- 顶栏 -->
    <header class="hd">
      <div>
        <h1>记录</h1>
        <p class="date">{{ today }} · 今日</p>
      </div>
      <Mascot type="momo" variant="avatar" :size="40" />
    </header>

    <!-- 小提示（AI 入口） -->
    <button class="ai-bar" @click="goChat">
      <span class="ai-ic">✦</span>
      <span class="ai-txt">说一句"午餐吃了鸡胸肉"，Momo 帮你结构化</span>
      <span class="ai-arrow">›</span>
    </button>

    <!-- 记录入口列表 -->
    <section class="list">
      <button
        v-for="it in items"
        :key="it.key"
        class="item"
        @click="openRecord(it)"
      >
        <div
          class="ic"
          :style="{ background: it.color, borderColor: it.accent }"
        >
          <span class="emoji">{{ it.emoji }}</span>
        </div>
        <div class="main">
          <p class="label">{{ it.label }}</p>
          <p class="sub">{{ it.sub }}</p>
        </div>
        <div class="side">
          <p class="summary" :style="{ color: it.accent }">
            {{ it.summary }}
          </p>
          <span class="arrow">›</span>
        </div>
      </button>
    </section>

    <!-- Momo 底部鼓励 -->
    <div class="encourage">
      <Mascot type="momo" variant="avatar" :size="40" />
      <p>每天记录一点点，小黑米 会越来越懂你 💪</p>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
    </transition>
  </div>
</template>

<style scoped>
.rec {
  padding-bottom: 24px;
}

/* 顶栏 */
.hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2px 18px;
}
.hd h1 {
  font-size: 24px;
  font-weight: 900;
  color: var(--text-1);
}
.date {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 4px;
}

/* AI 快速提示条 */
.ai-bar {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 14px;
  margin-bottom: 14px;
  background: linear-gradient(135deg, #f0f7ff 0%, var(--bg-elevated) 100%);
  border: 2px solid var(--brand-light);
  border-radius: 999px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
}
.ai-ic {
  color: var(--brand);
  font-size: 14px;
  flex-shrink: 0;
}
.ai-txt {
  flex: 1;
  text-align: left;
  font-size: 12px;
  color: var(--text-2);
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ai-arrow {
  color: var(--brand);
  font-size: 18px;
  font-weight: 800;
  flex-shrink: 0;
}

/* 记录入口列表 */
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 14px;
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  text-align: left;
  transition: transform 0.1s, box-shadow 0.1s;
  width: 100%;
}
.item:active {
  transform: translateY(2px);
  box-shadow: 0 0 0 var(--glass-border);
}
.ic {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  border: 2px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.emoji {
  font-size: 24px;
  line-height: 1;
}
.main {
  flex: 1;
  min-width: 0;
}
.label {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-1);
  margin-bottom: 2px;
}
.sub {
  font-size: 12px;
  color: var(--text-3);
}
.side {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.summary {
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}
.arrow {
  color: var(--text-3);
  font-size: 20px;
}

/* 底部鼓励条 */
.encourage {
  margin-top: 18px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-elevated);
  border: 1.5px dashed var(--glass-border);
  border-radius: 14px;
}
.encourage p {
  font-size: 12px;
  color: var(--text-2);
  font-weight: 600;
}

/* Toast */
.toast {
  position: fixed;
  left: 50%;
  bottom: 110px;
  transform: translateX(-50%);
  background: rgba(60, 60, 60, 0.9);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  padding: 10px 18px;
  border-radius: 999px;
  z-index: 30;
  pointer-events: none;
  white-space: nowrap;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.22s, transform 0.22s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(6px);
}
</style>
