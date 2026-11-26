<script setup lang="ts">
/**
 * Dashboard 首页 · Keep 风格改版
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Mascot from "../components/Mascot.vue";

// ✅ 1. API：全部真接口
import { getRecordSummary, type RecordSummary } from "../api/record";
import { listDietLogs, listWorkoutLogs } from "../api/logs";
import type { DietLogOut, WorkoutLogOut } from "../api/types";

const router = useRouter();

// ─────────────────────────── 常量（暂时写死，Round 2 从 profile 推） ───────────────────────────
// TODO(Round 2): 这几个目标值应该根据画像(BMR + 目标减脂速度)算出来，从 /profile 读 or 后端 summary 带出
const DIET_TARGET_KCAL = 1800;
const WATER_TARGET_ML = 2000;
// 1800 kcal × 50% / 4 = 225g 碳水；×20% / 4 = 90g 蛋白；×30% / 9 = 60g 脂肪
const NUTRI_TARGET = { carbs: 225, protein: 90, fat: 60 };

// ─────────────────────────── 响应式状态 ───────────────────────────
const loading = ref(true);
const errorMsg = ref<string | null>(null);

const summary = ref<RecordSummary | null>(null);
const dietLogs = ref<DietLogOut[]>([]);
const workoutLogs = ref<WorkoutLogOut[]>([]);
const WORKOUT_ICONS = { cardio: "🏃", stretch: "🧘", strength: "🏋️" } as const;

// ─────────────────────────── 数据加载 ───────────────────────────
function todayISO(): string {
  // "YYYY-MM-DD"，和后端 log_date 字段格式对齐
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

async function loadAll(): Promise<void> {
  loading.value = true;
  errorMsg.value = null;
  try {
    const [s, d, w] = await Promise.all([
      getRecordSummary(),
      listDietLogs(todayISO()),
      listWorkoutLogs(todayISO()),
    ]);
    summary.value = s;
    dietLogs.value = d;
    workoutLogs.value = w;
    console.log("summary, dietLogs, workoutLogs:", s, d, w);
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
    summary.value = null;
    dietLogs.value = [];
    workoutLogs.value = [];
    console.error("[Dashboard] loadAll failed:", e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadAll();
});

// ─────────────────────────── 日期显示 ───────────────────────────
const today = computed(() => {
  const d = new Date();
  return `${d.getMonth() + 1}月${d.getDate()}日`;
});

// ─────────────────────────── 饮食：热量 / 评分 / 半圆仪表 ───────────────────────────
//  从 summary.diet.kcal 取当日摄入，null 时取 0
const dietIntake = computed<number>(() => {
  return summary.value?.diet?.kcal ?? 0;
});

const dietTarget = DIET_TARGET_KCAL;

const dietScore = computed(() => {
  const ratio = Math.min(dietIntake.value / dietTarget, 1);
  return Math.round(ratio * 100);
});

const dietLevel = computed(() => {
  if (dietScore.value >= 80) return { label: "优秀", color: "var(--success)" };
  if (dietScore.value >= 50) return { label: "一般", color: "var(--warning)" };
  return { label: "偏低", color: "var(--danger)" };
});

// 半圆仪表（原样保留）
const gaugeR = 120;
const gaugeCirc = Math.PI * gaugeR;
const gaugeOffset = computed(() =>
  Math.round(gaugeCirc * (1 - dietScore.value / 100))
);

// ─────────────────────────── 三大素：从 dietLogs 累加 ───────────────────────────
//  从 dietLogs 里 reduce 累加 carbs_g / protein_g / fat_g
//   - 字段可能是 null（用户只填了食物名没填营养），用 ?? 0 兜底
//   - 四舍五入到整数再展示
const nutrients = computed(() => {
  const totals = dietLogs.value.reduce(
    (acc, log) => ({
      carbs: acc.carbs + (log.carbs_g ?? 0),
      protein: acc.protein + (log.protein_g ?? 0),
      fat: acc.fat + (log.fat_g ?? 0),
    }),
    { carbs: 0, protein: 0, fat: 0 }
  );
  return [
    {
      label: "碳水",
      used: Math.round(totals.carbs),
      total: NUTRI_TARGET.carbs,
      unit: "克",
      color: "#FF9F6B",
    },
    {
      label: "蛋白质",
      used: Math.round(totals.protein),
      total: NUTRI_TARGET.protein,
      unit: "克",
      color: "#58CC02",
    },
    {
      label: "脂肪",
      used: Math.round(totals.fat),
      total: NUTRI_TARGET.fat,
      unit: "克",
      color: "#3B82F6",
    },
  ];
});

// 饼图数据（原样保留，依赖上面的 nutrients）
const pieData = computed(() => {
  const total = nutrients.value.reduce((s, n) => s + Math.max(n.used, 1), 0);
  let acc = 0;
  return nutrients.value.map((n) => {
    const value = Math.max(n.used, 1);
    const start = acc / total;
    acc += value;
    const end = acc / total;
    return { ...n, start, end };
  });
});

// ─────────────────────────── 饮水 ───────────────────────────
//  从 summary.water 取；null 时取 0
const waterDrunk = computed<number>(() => {
  return summary.value?.water?.ml ?? 0;
});
const waterTarget = computed<number>(() => {
  return summary.value?.water?.target_ml ?? WATER_TARGET_ML;
});

// ─────────────────────────── 今日训练：从 workoutLogs 派生 ───────────────────────────
function classifyWorkout(type: string): "cardio" | "stretch" | "strength" {
  // TODO: 实现分类
  if (type.includes("跑") || type.includes("骑") || type.includes("有氧")) {
    return "cardio";
  }
  if (type.includes("拉伸") || type.includes("瑜伽")) {
    return "stretch";
  }
  return "strength";
}

const workoutsToday = computed(() => {
  return workoutLogs.value.map((w) => {
    const type = classifyWorkout(w.workout_type);
    const icon = WORKOUT_ICONS[type];
    return {
      id: w.id,
      type,
      icon,
      name: w.workout_type,
      meta: [`${w.duration_min}分钟`, w.intensity ?? "中等"],
      done: true,
      estKcal: 0,
    };
  });
});

const workoutDoneCount = computed(
  () => workoutsToday.value.filter((w) => w.done).length
);
const workoutTotalKcal = computed(() =>
  workoutsToday.value.reduce((s, w) => s + w.estKcal, 0)
);

// ─────────────────────────── 快速汇总摘要 ───────────────────────────
// 根据实际 used/target 比例动态判定标签
//   - diet: ratio = dietIntake / dietTarget
//       ratio < 0.5 → 偏低(danger) / 0.5-0.9 → 适中(success) / >0.9 → 充足(success) / >1.1 → 偏多(warning)
//   - 碳水/蛋白/脂肪 同理，各自比 target
//   提示：抽一个 helper function judgeLevel(used, target) → { value, color }
function judgeLevel(
  used: number,
  target: number
): { value: string; color: string } {
  // TODO: 实现
  const ratio = used / target;
  if (ratio < 0.5) return { value: "偏低", color: "var(--danger)" };
  if (ratio <= 0.9) return { value: "适中", color: "var(--success)" };
  if (ratio <= 1.1) return { value: "充足", color: "var(--success)" };
  return { value: "偏多", color: "var(--warning)" };
}

const summaryItems = computed(() => {
  const n = nutrients.value;
  return [
    { label: "饮食摄入", ...judgeLevel(dietIntake.value, dietTarget) },
    { label: "碳水", ...judgeLevel(n[0].used, n[0].total) },
    { label: "蛋白质", ...judgeLevel(n[1].used, n[1].total) },
    { label: "脂肪", ...judgeLevel(n[2].used, n[2].total) },
  ];
});

// ─────────────────────────── 路由跳转 ───────────────────────────
function goChat(): void {
  router.push({ name: "chat" });
}
function addData(): void {
  router.push({ name: "diet" });
}
function startWorkout(): void {
  router.push({ name: "chat" });
}
</script>

<template>
  <div class="dash">
    <!-- ========== 顶部日期切换 ========== -->
    <header class="hd">
      <button class="iconbtn">‹</button>
      <div class="date-pill">
        <span class="arrow">◂</span>
        <span class="date-txt">{{ today }}</span>
        <span class="arrow">▸</span>
      </div>
      <div class="user-slot">
        <Mascot type="momo" variant="avatar" :size="36" />
      </div>
    </header>
    <div v-if="loading" class="loading-hint">加载中…</div>
    <div v-else-if="errorMsg" class="error-hint" @click="loadAll">
      加载失败：{{ errorMsg }}，点击重试
    </div>
    <div v-else>
      <!-- ========== 半圆饮食评分 ========== -->
      <div class="gauge-wrap">
        <svg
          viewBox="0 0 280 160"
          class="gauge"
          preserveAspectRatio="xMidYMid meet"
        >
          <!-- 背景半环 -->
          <path
            d="M 20 140 A 120 120 0 0 1 260 140"
            fill="none"
            stroke="var(--glass-border)"
            stroke-width="14"
            stroke-linecap="round"
          />
          <!-- 填充半环 -->
          <path
            d="M 20 140 A 120 120 0 0 1 260 140"
            fill="none"
            :stroke="dietLevel.color"
            stroke-width="14"
            stroke-linecap="round"
            :stroke-dasharray="gaugeCirc"
            :stroke-dashoffset="gaugeOffset"
            style="transition: stroke-dashoffset 0.6s ease-out"
          />
        </svg>
        <div class="gauge-center">
          <p class="gauge-tag">
            <span class="dot" :style="{ background: dietLevel.color }"></span>
            饮食
          </p>
          <p class="gauge-score">
            {{ dietScore }}<span class="unit">分</span>
            <span class="info-ic">ⓘ</span>
          </p>
        </div>
      </div>

      <!-- ========== 营养摘要 ========== -->
      <div class="summary">
        <div v-for="(item, i) in summaryItems" :key="i" class="sum-item">
          <span class="sum-k">{{ item.label }}</span>
          <span class="sum-v" :style="{ color: item.color }">{{
            item.value
          }}</span>
        </div>
      </div>

      <!-- ========== AI 洞察 ========== -->
      <button class="card ai-card" @click="goChat">
        <div class="ai-head">
          <span class="ai-dot">✦</span>
          <span class="ai-title-sm">AI 洞察</span>
        </div>
        <p class="ai-main">记录今日的饮食，获取饮食结构详细分析</p>
        <div class="ai-foot">
          <div class="meal-chip">
            <Mascot
              type="momo"
              variant="avatar"
              :size="36"
              class="meal-mascot"
            />
            <div class="meal-info">
              <p class="meal-name">加餐</p>
              <p class="meal-sub">记录今天的第一餐</p>
            </div>
          </div>
          <span class="meal-btn">
            <span class="plus">+</span>
            记录
          </span>
        </div>
      </button>

      <!-- ========== 饮食摄入 三栏 ========== -->
      <div class="card">
        <div class="section-head">
          <span class="section-ic">🍴</span>
          <span class="section-title">饮食摄入</span>
        </div>
        <div class="intake-row">
          <div class="intake-col left">
            <p class="intake-label">饮食摄入</p>
            <p class="intake-val">{{ dietIntake }}</p>
            <p class="intake-unit">千卡</p>
          </div>
          <div class="intake-col center">
            <svg viewBox="0 0 100 60" class="half-ring">
              <path
                d="M 10 50 A 40 40 0 0 1 90 50"
                fill="none"
                stroke="var(--glass-border)"
                stroke-width="8"
                stroke-linecap="round"
              />
              <path
                d="M 10 50 A 40 40 0 0 1 90 50"
                fill="none"
                stroke="var(--brand)"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="125"
                :stroke-dashoffset="125 * 0.22"
              />
            </svg>
            <p class="intake-label">还可摄入 <span class="info-ic">ⓘ</span></p>
            <p class="intake-val big">{{ dietTarget - dietIntake }}</p>
            <p class="intake-sub">推荐摄入 {{ dietTarget }}</p>
          </div>
          <div class="intake-col right">
            <p class="intake-label">运动消耗</p>
            <p class="intake-val">0</p>
            <p class="intake-unit">千卡</p>
          </div>
        </div>
      </div>

      <!-- ========== 营养成分 ========== -->
      <div class="card">
        <div class="section-head">
          <span class="section-ic">🧪</span>
          <span class="section-title">营养成分</span>
        </div>
        <div class="nutri-row">
          <div v-for="n in nutrients" :key="n.label" class="nutri-col">
            <p class="nutri-label">{{ n.label }}</p>
            <p class="nutri-val">
              {{ n.used }}<span class="divider">/</span>{{ n.total }}
              {{ n.unit }}
            </p>
            <div class="nutri-bar">
              <div
                class="nutri-fill"
                :style="{
                  width: `${Math.min((n.used / n.total) * 100, 100)}%`,
                  background: n.color,
                }"
              ></div>
            </div>
          </div>
        </div>
        <div class="nutri-chart-row">
          <div class="nutri-legend">
            <div v-for="n in nutrients" :key="n.label" class="legend-item">
              <span class="legend-dot" :style="{ background: n.color }"></span>
              <span class="legend-label">{{ n.label }}</span>
              <span class="legend-pct">0.0%</span>
            </div>
          </div>
          <div class="donut">
            <svg viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="var(--glass-border)"
                stroke-width="12"
              />
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="#DBEAFE"
                stroke-width="12"
                stroke-dasharray="80 240"
                transform="rotate(-90 50 50)"
              />
            </svg>
          </div>
        </div>
        <div class="empty-state">
          <p class="empty-title">暂无数据</p>
          <p class="empty-sub">请先点击下方「添加数据」记录今天的第一餐吧</p>
        </div>
      </div>

      <!-- ========== 饮水 ========== -->
      <div class="card water-card">
        <div class="section-head">
          <span class="section-ic">🥤</span>
          <span class="section-title">饮水</span>
          <span class="section-arrow">›</span>
        </div>
        <div class="water-row">
          <div class="water-info">
            <p class="water-val">
              <span class="water-num">{{ waterDrunk }}</span> /
              {{ waterTarget }} 毫升
            </p>
          </div>
          <div class="water-bottle">💧</div>
        </div>
      </div>

      <!-- ========== 今日训练 ========== -->
      <div class="card">
        <div class="section-head">
          <span class="section-ic">🏋️</span>
          <span class="section-title">今日训练</span>
          <span class="section-arrow">›</span>
        </div>

        <!-- 空状态 -->
        <div v-if="workoutsToday.length === 0" class="workout-empty">
          <p class="we-main">还没有训练计划</p>
          <p class="we-sub">去问 小黑米AI教练 给你安排一份今日训练 →</p>
          <button class="we-btn" @click="goChat">
            <Mascot type="momo" variant="avatar" :size="20" />
            去问 小黑米 AI 教练
          </button>
        </div>

        <!-- 有计划 -->
        <template v-else>
          <div class="workout-list">
            <div
              v-for="w in workoutsToday"
              :key="w.id"
              class="workout-item"
              :class="[w.type, { done: w.done }]"
            >
              <div class="wi-icon">{{ w.icon }}</div>
              <div class="wi-main">
                <p class="wi-name">{{ w.name }}</p>
                <p class="wi-meta">
                  <template v-for="(m, i) in w.meta" :key="i">
                    <span>{{ m }}</span>
                    <span v-if="i < w.meta.length - 1" class="wi-dot"></span>
                  </template>
                </p>
              </div>
              <span v-if="w.done" class="wi-check">✓</span>
              <span v-else class="wi-badge">去训练</span>
            </div>
          </div>
          <div class="workout-summary">
            <p class="ws-text">
              今日
              <strong
                >{{ workoutDoneCount }} /
                {{ workoutsToday.length }} 完成</strong
              >
              · 预计消耗 {{ workoutTotalKcal }} 千卡
            </p>
            <button class="ws-btn" @click="startWorkout">开始训练</button>
          </div>
        </template>
      </div>

      <!-- ========== 推广 banner ========== -->
      <div class="banner">
        <div class="banner-info">
          <p class="banner-title">你的饮食结构合理吗？</p>
          <p class="banner-sub">1 分钟定制你的专属饮食方案</p>
          <button class="banner-btn" @click="goChat">开启减重计划</button>
        </div>
        <div class="banner-img">🥗</div>
      </div>

      <!-- 占位，避免被 FAB 挡 -->
      <div style="height: 80px"></div>

      <!-- ========== 底部 FAB ========== -->
      <button class="fab" @click="addData">
        <span class="fab-pen">✎</span>
        <span>添加数据</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.dash {
  padding-bottom: 24px;
}

/* 顶栏 */
.hd {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0 14px;
}
.iconbtn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 26px;
  color: var(--text-1);
  cursor: pointer;
}
.date-pill {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  padding: 8px 18px;
  border-radius: 999px;
  box-shadow: var(--shadow-sm);
}
.date-pill .arrow {
  color: var(--text-3);
  font-size: 12px;
  cursor: pointer;
}
.date-pill .date-txt {
  font-size: 14px;
  font-weight: 800;
}
.user-slot {
  flex-shrink: 0;
}

/* 半圆仪表 */
.gauge-wrap {
  position: relative;
  width: 100%;
  margin: 10px 0 14px;
  display: flex;
  justify-content: center;
}
.gauge {
  width: 90%;
  max-width: 320px;
  height: auto;
}
.gauge-center {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  padding-bottom: 10px;
}
.gauge-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 15px;
  font-weight: 800;
  color: var(--success);
}
.gauge-tag .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.gauge-score {
  font-size: 34px;
  font-weight: 900;
  color: var(--text-1);
  margin-top: 4px;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}
.gauge-score .unit {
  font-size: 14px;
  color: var(--text-3);
  font-weight: 500;
}
.gauge-score .info-ic {
  font-size: 13px;
  color: var(--text-4);
  margin-left: 2px;
}

/* 营养摘要 */
.summary {
  display: flex;
  justify-content: space-around;
  padding: 10px 4px 20px;
  border-bottom: 1px solid var(--glass-border);
  margin-bottom: 16px;
}
.sum-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}
.sum-k {
  color: var(--text-3);
}
.sum-v {
  font-weight: 800;
}

/* 卡片基础 */
.card {
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 16px;
  margin-bottom: 14px;
}
.section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 800;
}
.section-ic {
  font-size: 18px;
}
.section-title {
  flex: 1;
}
.section-arrow {
  color: var(--text-3);
  font-size: 20px;
  margin-left: auto;
}

/* AI 卡片 */
.ai-card {
  background: linear-gradient(135deg, #f0f7ff 0%, var(--bg-elevated) 100%);
  border-color: var(--brand-light);
  box-shadow: var(--shadow-primary);
  cursor: pointer;
  text-align: left;
  width: 100%;
}
.ai-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--brand-dark);
  font-weight: 800;
  margin-bottom: 12px;
}
.ai-dot {
  font-size: 16px;
}
.ai-main {
  font-size: 17px;
  font-weight: 800;
  line-height: 1.4;
  color: var(--text-1);
  margin-bottom: 14px;
}
.ai-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.meal-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}
.meal-mascot {
  border: 2px solid var(--success);
}
.meal-info {
  line-height: 1.3;
}
.meal-name {
  font-size: 14px;
  font-weight: 800;
}
.meal-sub {
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
}
.meal-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: 999px;
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  font-size: 13px;
  font-weight: 700;
  color: var(--text-1);
  box-shadow: var(--shadow-sm);
}
.meal-btn .plus {
  background: var(--text-1);
  color: #fff;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 900;
}

/* 饮食摄入三栏 */
.intake-row {
  display: grid;
  grid-template-columns: 1fr 1.3fr 1fr;
  align-items: end;
  gap: 10px;
}
.intake-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.intake-col.center {
  padding: 0 6px;
}
.half-ring {
  width: 110px;
  height: 56px;
  margin-bottom: 2px;
}
.intake-label {
  font-size: 12px;
  color: var(--text-3);
}
.intake-val {
  font-size: 24px;
  font-weight: 900;
  color: var(--text-1);
  line-height: 1.1;
}
.intake-val.big {
  font-size: 28px;
  color: var(--brand-dark);
}
.intake-unit {
  font-size: 11px;
  color: var(--text-3);
}
.intake-sub {
  font-size: 11px;
  color: var(--text-3);
}
.info-ic {
  font-size: 11px;
  color: var(--text-4);
}

/* 营养成分 */
.nutri-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 14px;
  margin-bottom: 20px;
}
.nutri-col {
}
.nutri-label {
  font-size: 12px;
  color: var(--text-3);
  margin-bottom: 2px;
}
.nutri-val {
  font-size: 14px;
  font-weight: 800;
  margin-bottom: 6px;
}
.nutri-val .divider {
  color: var(--text-4);
  margin: 0 1px;
  font-weight: 500;
}
.nutri-bar {
  height: 6px;
  background: var(--glass-border);
  border-radius: 999px;
  overflow: hidden;
}
.nutri-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s;
}
.nutri-chart-row {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-top: 4px;
}
.nutri-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
.legend-label {
  flex: 1;
  color: var(--text-1);
  font-weight: 500;
}
.legend-pct {
  color: var(--text-3);
}
.donut {
  width: 80px;
  height: 80px;
}
.donut svg {
  width: 100%;
  height: 100%;
}

.empty-state {
  text-align: center;
  padding: 20px 0 4px;
  margin-top: 10px;
  border-top: 1px dashed var(--glass-border);
}
.empty-title {
  font-size: 13px;
  color: var(--text-3);
  margin-bottom: 4px;
}
.empty-sub {
  font-size: 11px;
  color: var(--text-4);
}

/* 饮水 */
.water-card .section-head {
  margin-bottom: 12px;
}
.water-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.water-val {
  font-size: 14px;
  color: var(--text-3);
}
.water-val .water-num {
  font-size: 26px;
  font-weight: 900;
  color: var(--text-1);
  margin-right: 4px;
}
.water-bottle {
  font-size: 48px;
}

/* 今日训练 */
.workout-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.workout-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--bg-app);
  border: 1.5px solid var(--glass-border);
  border-radius: 14px;
}
.workout-item.done {
  background: #f0fdf4;
  border-color: #bbf7d0;
}
.wi-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background: var(--brand-light);
}
.workout-item.strength .wi-icon {
  background: #fee2e2;
}
.workout-item.cardio .wi-icon {
  background: #dbeafe;
}
.workout-item.stretch .wi-icon {
  background: #fef3c7;
}
.wi-main {
  flex: 1;
  min-width: 0;
}
.wi-name {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-1);
  margin-bottom: 2px;
}
.wi-meta {
  font-size: 11px;
  color: var(--text-3);
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.wi-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--text-4);
}
.wi-badge {
  font-size: 11px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 10px;
  color: var(--brand);
  background: var(--brand-light);
  flex-shrink: 0;
}
.wi-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--success, #58cc02);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 900;
  flex-shrink: 0;
}
.workout-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--glass-border);
}
.ws-text {
  font-size: 12px;
  color: var(--text-3);
}
.ws-text strong {
  color: var(--success, #58cc02);
  font-weight: 800;
}
.ws-btn {
  background: var(--brand);
  color: #fff;
  border: none;
  font-size: 12px;
  font-weight: 800;
  padding: 7px 14px;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 2px 0 var(--brand-dark);
}
.ws-btn:active {
  transform: translateY(1px);
  box-shadow: none;
}
.workout-empty {
  text-align: center;
  padding: 20px 10px 10px;
}
.we-main {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-1);
  margin-bottom: 4px;
}
.we-sub {
  font-size: 12px;
  color: var(--text-3);
  margin-bottom: 14px;
}
.we-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--brand-light);
  color: var(--brand-dark);
  border: 1.5px solid var(--brand);
  border-radius: 999px;
  padding: 6px 14px 6px 6px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

/* 推广 banner */
.banner {
  background: linear-gradient(135deg, #fff4cc 0%, #ffecb3 100%);
  border: 2px solid var(--warning);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 0 #d18800;
  margin-bottom: 14px;
}
.banner-info {
  flex: 1;
}
.banner-title {
  font-size: 15px;
  font-weight: 800;
  color: #4a3200;
  margin-bottom: 2px;
}
.banner-sub {
  font-size: 11px;
  color: #8a6700;
  margin-bottom: 10px;
}
.banner-btn {
  background: #ff6b35;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 2px 0 #c64a1e;
}
.banner-img {
  font-size: 48px;
}

/* FAB 底部悬浮按钮 */
.fab {
  position: fixed;
  left: 50%;
  bottom: 76px; /* 让出底部 tabbar 高度 */
  transform: translateX(-50%);
  z-index: 10;
  background: var(--success);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 14px 36px;
  font-size: 16px;
  font-weight: 800;
  box-shadow: 0 4px 0 #46a302, 0 8px 20px rgba(88, 204, 2, 0.3);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.1s;
}
.fab:active {
  transform: translateX(-50%) translateY(2px);
  box-shadow: 0 2px 0 #46a302, 0 4px 10px rgba(88, 204, 2, 0.3);
}
.fab-pen {
  font-size: 16px;
}
.loading-hint,
.error-hint {
  text-align: center;
  padding: 20px;
  color: var(--text-3);
  font-size: 14px;
}
.error-hint {
  color: var(--danger);
  cursor: pointer;
}
</style>
