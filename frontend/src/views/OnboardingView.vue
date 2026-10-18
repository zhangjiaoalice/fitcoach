<script setup lang="ts">
/**
 * Onboarding 新手引导页
 *   - 用户注册/首次登录后强制进入
 *   - 3 步问卷式：认识你 / 身材 / 目标
 *   - 完成后 upsertProfile 提交 → 跳 /dashboard
 */
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { upsertProfile } from "../api/profile";
import { ApiError } from "../api/client";
import { setProfileCompleted } from "../router";
import type { ProfileUpsert } from "../api/types";

const router = useRouter();

// 当前步骤：1 认识 / 2 身材 / 3 目标 / 4 完成庆祝
const step = ref<1 | 2 | 3 | 4>(1);
const loading = ref(false);
const errorMsg = ref("");

// 表单状态（对齐 ProfileUpsert 字段）
const form = ref({
  nickname: "", // 后端 model 没有，先存 goal_description 或忽略
  gender: "female" as "male" | "female",
  age: 27,
  height_cm: 165,
  current_weight_kg: 58.2,
  target_weight_kg: 54,
  // activity_level 字段：low / medium / high
  activity_level: "medium" as "low" | "medium" | "high",
  // training_days_per_week 对应 "每周练几次"
  training_days_per_week: 3,
  // 多选饮食偏好拼成字符串
  diet_tags: [] as string[],
  // 训练目标（没对应后端字段，塞进 goal_description）
  goal: "lose_fat" as "lose_fat" | "gain_muscle" | "tone",
});

// activity_level 和 training_days_per_week 的对应
const freqOptions = [
  { label: "1-2 次", emoji: "🚶", sub: "轻度", days: 2, activity: "low" },
  { label: "3-4 次", emoji: "🏃", sub: "适中", days: 4, activity: "medium" },
  { label: "5+ 次", emoji: "🏋️", sub: "硬核", days: 5, activity: "high" },
] as const;

const goalOptions = [
  { value: "lose_fat", emoji: "🔥", label: "减脂", sub: "减少体脂" },
  { value: "gain_muscle", emoji: "💪", label: "增肌", sub: "长肌肉" },
  { value: "tone", emoji: "✨", label: "塑形", sub: "线条感" },
] as const;

const dietOptions = [
  { tag: "高蛋白", emoji: "🍗" },
  { tag: "低碳水", emoji: "🥦" },
  { tag: "素食", emoji: "🌱" },
  { tag: "戒糖", emoji: "🚫" },
  { tag: "无乳糖", emoji: "🥛" },
  { tag: "无麸质", emoji: "🌾" },
];

// 校验每步能否进入下一步
const canNext = computed(() => {
  if (step.value === 1) {
    return !!form.value.gender && form.value.age >= 14 && form.value.age <= 80;
  }
  if (step.value === 2) {
    return (
      form.value.height_cm >= 100 &&
      form.value.height_cm <= 220 &&
      form.value.current_weight_kg >= 30 &&
      form.value.current_weight_kg <= 200 &&
      form.value.target_weight_kg >= 30 &&
      form.value.target_weight_kg <= 200
    );
  }
  if (step.value === 3) {
    return !!form.value.goal && !!form.value.activity_level;
  }
  return true;
});

function next(): void {
  if (!canNext.value) return;
  if (step.value < 3) {
    step.value = (step.value + 1) as 1 | 2 | 3;
    return;
  }
  // Step 3 → 提交
  submit();
}

function back(): void {
  if (step.value === 4) return; // 完成页不许返回
  if (step.value === 1) {
    // 第一步返回退回 /login（给用户后悔的机会）
    router.replace({ name: "login" });
    return;
  }
  step.value = (step.value - 1) as 1 | 2 | 3;
}

function stepValue(
  key: keyof typeof form.value,
  delta: number,
  min: number,
  max: number
): void {
  const curr = form.value[key] as number;
  const next = Math.max(min, Math.min(max, curr + delta));
  (form.value[key] as number) = Number(next.toFixed(1));
}

function pickFreq(idx: number): void {
  const option = freqOptions[idx];
  form.value.activity_level = option.activity;
  form.value.training_days_per_week = option.days;
}

function toggleDiet(tag: string): void {
  const i = form.value.diet_tags.indexOf(tag);
  if (i === -1) form.value.diet_tags.push(tag);
  else form.value.diet_tags.splice(i, 1);
}

async function submit(): Promise<void> {
  loading.value = true;
  errorMsg.value = "";
  const payload: ProfileUpsert = {
    gender: form.value.gender,
    age: form.value.age,
    height_cm: form.value.height_cm,
    current_weight_kg: form.value.current_weight_kg,
    target_weight_kg: form.value.target_weight_kg,
    activity_level: form.value.activity_level,
    training_days_per_week: form.value.training_days_per_week,
    diet_preference: form.value.diet_tags.join(","),
    goal_description: form.value.goal,
  };
  try {
    await upsertProfile(payload);
    setProfileCompleted(true); // 更新守卫缓存，避免再被弹回 onboarding
    step.value = 4; // 进入完成页
  } catch (err) {
    errorMsg.value = err instanceof ApiError ? err.message : "提交失败，请重试";
  } finally {
    loading.value = false;
  }
}

function finish(): void {
  router.replace({ name: "chat" });
}

// 为了庆祝页的汇总显示
const diffWeight = computed(() => {
  const d = form.value.target_weight_kg - form.value.current_weight_kg;
  return d > 0 ? `+${d.toFixed(1)}` : d.toFixed(1);
});
const goalLabel = computed(
  () => goalOptions.find((o) => o.value === form.value.goal)?.label ?? ""
);
const freqLabel = computed(
  () =>
    freqOptions.find((o) => o.activity === form.value.activity_level)?.label ??
    ""
);
</script>

<template>
  <div class="ob-wrap">
    <!-- ========== 顶栏（1-3 步才显示） ========== -->
    <div v-if="step < 4" class="topbar">
      <button class="back" @click="back">←</button>
      <div class="progress">
        <div
          class="seg"
          :class="step > 1 ? 'done' : step === 1 ? 'now' : ''"
        ></div>
        <div
          class="seg"
          :class="step > 2 ? 'done' : step === 2 ? 'now' : ''"
        ></div>
        <div
          class="seg"
          :class="step > 3 ? 'done' : step === 3 ? 'now' : ''"
        ></div>
      </div>
      <span class="step-txt">{{ step }}/3</span>
    </div>

    <!-- ========== Step 1 认识你 ========== -->
    <div v-if="step === 1" class="screen">
      <div class="momo-row">
        <div class="momo-avatar">
          <img src="/mascots/momo-avatar.png" alt="Momo" />
        </div>
        <div class="speech">嗨～我是 Momo 💕<br />先让我认识一下你吧！</div>
      </div>

      <h2 class="q">👫 你的性别是？</h2>
      <div class="choice-grid cols-2">
        <div
          class="choice"
          :class="{ selected: form.gender === 'female' }"
          @click="form.gender = 'female'"
        >
          <span class="emoji">👩</span>
          <span class="lbl">女生</span>
        </div>
        <div
          class="choice"
          :class="{ selected: form.gender === 'male' }"
          @click="form.gender = 'male'"
        >
          <span class="emoji">👨</span>
          <span class="lbl">男生</span>
        </div>
      </div>

      <h2 class="q">🎂 你今年多大？</h2>
      <div class="stepper">
        <button class="step-btn" @click="stepValue('age', -1, 14, 80)">
          −
        </button>
        <div class="val">{{ form.age }}<span class="unit">岁</span></div>
        <button class="step-btn" @click="stepValue('age', 1, 14, 80)">+</button>
      </div>
    </div>

    <!-- ========== Step 2 身材 ========== -->
    <div v-else-if="step === 2" class="screen">
      <div class="momo-row">
        <div class="momo-avatar">
          <img src="/mascots/momo-avatar.png" alt="Momo" />
        </div>
        <div class="speech">这个数据只有我们俩知道～<br />放心告诉我 ✨</div>
      </div>

      <h2 class="q">📏 你的身高是？</h2>
      <div class="stepper">
        <button class="step-btn" @click="stepValue('height_cm', -1, 100, 220)">
          −
        </button>
        <div class="val">{{ form.height_cm }}<span class="unit">cm</span></div>
        <button class="step-btn" @click="stepValue('height_cm', 1, 100, 220)">
          +
        </button>
      </div>

      <h2 class="q">⚖️ 当前体重？</h2>
      <div class="stepper">
        <button
          class="step-btn"
          @click="stepValue('current_weight_kg', -0.1, 30, 200)"
        >
          −
        </button>
        <div class="val">
          {{ form.current_weight_kg.toFixed(1) }}<span class="unit">kg</span>
        </div>
        <button
          class="step-btn"
          @click="stepValue('current_weight_kg', 0.1, 30, 200)"
        >
          +
        </button>
      </div>

      <h2 class="q">🎯 目标体重？</h2>
      <div class="stepper">
        <button
          class="step-btn"
          @click="stepValue('target_weight_kg', -0.1, 30, 200)"
        >
          −
        </button>
        <div class="val success">
          {{ form.target_weight_kg.toFixed(1) }}<span class="unit">kg</span>
        </div>
        <button
          class="step-btn"
          @click="stepValue('target_weight_kg', 0.1, 30, 200)"
        >
          +
        </button>
      </div>
    </div>

    <!-- ========== Step 3 目标 ========== -->
    <div v-else-if="step === 3" class="screen">
      <div class="momo-row">
        <div class="momo-avatar">
          <img src="/mascots/momo-avatar.png" alt="Momo" />
        </div>
        <div class="speech">最后一步啦～<br />说说你的小目标 🎯</div>
      </div>

      <h2 class="q">🎯 你想要什么？</h2>
      <div class="choice-grid cols-3">
        <div
          v-for="opt in goalOptions"
          :key="opt.value"
          class="choice"
          :class="{ selected: form.goal === opt.value }"
          @click="form.goal = opt.value"
        >
          <span class="emoji">{{ opt.emoji }}</span>
          <span class="lbl">{{ opt.label }}</span>
          <span class="sub">{{ opt.sub }}</span>
        </div>
      </div>

      <h2 class="q">📅 一周能练几次？</h2>
      <div class="choice-grid cols-3">
        <div
          v-for="(opt, i) in freqOptions"
          :key="opt.label"
          class="choice"
          :class="{ selected: form.activity_level === opt.activity }"
          @click="pickFreq(i)"
        >
          <span class="emoji" style="font-size: 28px">{{ opt.emoji }}</span>
          <span class="lbl">{{ opt.label }}</span>
          <span class="sub">{{ opt.sub }}</span>
        </div>
      </div>

      <h2 class="q">🥗 饮食偏好（多选）</h2>
      <div class="chips">
        <div
          v-for="d in dietOptions"
          :key="d.tag"
          class="chip"
          :class="{ selected: form.diet_tags.includes(d.tag) }"
          @click="toggleDiet(d.tag)"
        >
          <span class="emoji">{{ d.emoji }}</span
          >{{ d.tag }}
        </div>
      </div>
    </div>

    <!-- ========== Step 4 完成庆祝 ========== -->
    <div v-else class="success-screen">
      <div class="confetti" style="left: 10%; animation-delay: 0s">🎉</div>
      <div class="confetti" style="left: 25%; animation-delay: 0.3s">✨</div>
      <div class="confetti" style="left: 40%; animation-delay: 0.6s">⭐</div>
      <div class="confetti" style="left: 55%; animation-delay: 0.9s">💪</div>
      <div class="confetti" style="left: 70%; animation-delay: 1.2s">🎊</div>
      <div class="confetti" style="left: 85%; animation-delay: 1.5s">💕</div>

      <div class="success-mascot">
        <img src="/mascots/momo-avatar.png" alt="Momo" />
      </div>
      <h2 class="success-title">欢迎加入 FitCoach！</h2>
      <p class="success-sub">我已经了解你啦<br />咱们一起冲向目标 💪✨</p>

      <div class="success-summary">
        <div class="row">
          <span class="k">👤 性别 · 年龄</span>
          <span class="v"
            >{{ form.gender === "female" ? "女生" : "男生" }} ·
            {{ form.age }} 岁</span
          >
        </div>
        <div class="row">
          <span class="k">📏 身高 · 体重</span>
          <span class="v"
            >{{ form.height_cm }}cm ·
            {{ form.current_weight_kg.toFixed(1) }}kg</span
          >
        </div>
        <div class="row">
          <span class="k">🎯 目标体重</span>
          <span class="v success-txt">
            {{ form.target_weight_kg.toFixed(1) }}kg ({{ diffWeight }}kg)
          </span>
        </div>
        <div class="row">
          <span class="k">🔥 训练目标</span>
          <span class="v">{{ goalLabel }} · 每周 {{ freqLabel }}</span>
        </div>
      </div>

      <button class="btn btn-success" @click="finish">开始冒险 🚀</button>
    </div>

    <!-- ========== 底部按钮（1-3 步） ========== -->
    <div v-if="step < 4" class="footer">
      <p v-if="errorMsg" class="err">{{ errorMsg }}</p>
      <button
        class="btn"
        :class="canNext ? 'btn-primary' : 'btn-disabled'"
        :disabled="!canNext || loading"
        @click="next"
      >
        {{ loading ? "提交中…" : step === 3 ? "完成 ✨" : "下一步 →" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.ob-wrap {
  height: 100vh;
  background: var(--bg-app);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶栏 */
.topbar {
  padding: 16px 20px 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-elevated);
}
.back {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  font-size: 24px;
  color: var(--text-3);
  cursor: pointer;
}
.progress {
  flex: 1;
  display: flex;
  gap: 6px;
}
.seg {
  flex: 1;
  height: 10px;
  background: var(--glass-border);
  border-radius: 999px;
}
.seg.done {
  background: linear-gradient(90deg, var(--success), #46a302);
}
.seg.now {
  background: linear-gradient(
    90deg,
    var(--success) 60%,
    var(--glass-border) 60%
  );
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
.step-txt {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-3);
}

/* 内容 */
.screen {
  flex: 1;
  overflow-y: auto;
  padding: 10px 24px 20px;
}

/* Momo 对白 */
.momo-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 20px;
}
.momo-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(180deg, #ffeeee 0%, #ffd5d5 100%);
  border: 3px solid var(--coral, #ff9ed2);
  overflow: hidden;
  flex-shrink: 0;
}
.momo-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
}
.speech {
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  padding: 12px 14px;
  border-radius: 16px;
  border-top-left-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  box-shadow: var(--shadow-sm);
  max-width: 220px;
  position: relative;
}
.speech::before {
  content: "";
  position: absolute;
  left: -8px;
  bottom: 10px;
  width: 10px;
  height: 10px;
  background: var(--bg-elevated);
  border-left: 2px solid var(--glass-border);
  border-bottom: 2px solid var(--glass-border);
  transform: rotate(45deg);
}

/* 问题标题 */
.q {
  font-size: 18px;
  font-weight: 800;
  margin: 16px 0 12px;
  letter-spacing: -0.01em;
}

/* 大卡片选项 */
.choice-grid {
  display: grid;
  gap: 10px;
  margin-bottom: 16px;
}
.choice-grid.cols-2 {
  grid-template-columns: 1fr 1fr;
}
.choice-grid.cols-3 {
  grid-template-columns: 1fr 1fr 1fr;
}
.choice {
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 16px 10px;
  text-align: center;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all 0.15s;
  user-select: none;
}
.choice:hover {
  transform: translateY(-2px);
}
.choice.selected {
  border-color: var(--brand);
  background: var(--brand-light);
  box-shadow: var(--shadow-primary);
}
.choice .emoji {
  font-size: 36px;
  display: block;
  margin-bottom: 6px;
}
.choice .lbl {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-1);
  display: block;
}
.choice .sub {
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
  display: block;
}

/* 数值 Stepper */
.stepper {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 10px 16px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 10px;
}
.step-btn {
  width: 44px;
  height: 44px;
  border: 2px solid var(--brand);
  background: var(--brand-light);
  color: var(--brand-dark);
  border-radius: 50%;
  font-size: 22px;
  font-weight: 900;
  cursor: pointer;
}
.step-btn:active {
  transform: translateY(1px);
}
.val {
  flex: 1;
  text-align: center;
  font-size: 32px;
  font-weight: 900;
  color: var(--brand-dark);
}
.val.success {
  color: var(--success);
}
.val .unit {
  font-size: 14px;
  color: var(--text-3);
  font-weight: 500;
  margin-left: 2px;
}

/* 多选 chip */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.chip {
  padding: 10px 14px;
  border: 2px solid var(--glass-border);
  border-radius: 999px;
  background: var(--bg-elevated);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s;
}
.chip.selected {
  border-color: var(--success);
  background: var(--success-light, #d7f7b4);
  color: #2e7d00;
}
.chip .emoji {
  margin-right: 4px;
}

/* 底部按钮 */
.footer {
  position: fixed;
  padding: 12px 24px 20px;
  background: var(--bg-elevated);
  width: 100%;
  bottom: 0;
  left: 0;
}
.err {
  color: var(--danger, #ff4b4b);
  font-size: 12px;
  margin-bottom: 8px;
  text-align: center;
}
.btn {
  display: block;
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.1s;
}
.btn:active:not(:disabled) {
  transform: translateY(2px);
}
.btn-primary {
  background: var(--brand);
  color: #fff;
  box-shadow: var(--shadow-primary);
}
.btn-primary:active {
  box-shadow: 0 0 0 var(--brand-dark);
}
.btn-success {
  background: var(--success);
  color: #fff;
  box-shadow: var(--shadow-success);
}
.btn-disabled {
  background: var(--glass-border);
  color: var(--text-4);
  cursor: not-allowed;
}

/* 完成页 */
.success-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.confetti {
  position: absolute;
  font-size: 24px;
  top: -40px;
  animation: fall 3s ease-in infinite;
  opacity: 0.9;
}
@keyframes fall {
  0% {
    transform: translateY(-40px) rotate(0deg);
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
  }
}
.success-mascot {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: linear-gradient(180deg, #ffeeee 0%, #ffd5d5 100%);
  border: 4px solid var(--coral, #ff9ed2);
  overflow: hidden;
  margin-bottom: 20px;
  position: relative;
  z-index: 2;
}
.success-mascot img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
}
.success-title {
  font-size: 24px;
  font-weight: 900;
  color: var(--brand-dark);
  margin-bottom: 10px;
  position: relative;
  z-index: 2;
}
.success-sub {
  color: var(--text-3);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
  position: relative;
  z-index: 2;
}
.success-summary {
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 24px;
  width: 100%;
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 2;
}
.success-summary .row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px dashed var(--glass-border);
}
.success-summary .row:last-child {
  border-bottom: none;
}
.success-summary .k {
  color: var(--text-3);
}
.success-summary .v {
  font-weight: 800;
  color: var(--text-1);
}
.success-summary .success-txt {
  color: var(--success);
}
</style>
