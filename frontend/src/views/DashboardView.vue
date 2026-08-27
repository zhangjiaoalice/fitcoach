<script setup lang="ts">
import { computed } from "vue";
import { profile, dashboard } from "../api/mock";
import Icon from "../components/Icon.vue";
import TrendChart from "../components/TrendChart.vue";

const rate = computed(() => Math.round((dashboard.workoutDone / dashboard.workoutPlanned) * 100));
// 进度环：周长 = 2πr，r=34 → ≈214；offset = 周长 * (1 - 完成比)
const R = 34;
const circ = Math.round(2 * Math.PI * R);
const dashOffset = computed(() => Math.round(circ * (1 - dashboard.workoutDone / dashboard.workoutPlanned)));
</script>

<template>
  <header class="hd">
    <div>
      <h1>今日概览</h1>
      <p>8 月 4 日 星期二</p>
    </div>
    <div class="av">{{ profile.initials }}</div>
  </header>

  <div class="grid2">
    <div class="mc glass">
      <p class="lb"><Icon name="scale" :size="13" color="var(--text-3)" />当前体重</p>
      <p class="nm">{{ dashboard.currentWeight }}<s>kg</s></p>
      <p class="sub" style="color: var(--brand-bright)">距目标 {{ dashboard.targetGap }}kg</p>
    </div>
    <div class="mc glass">
      <p class="lb"><Icon name="flame" :size="13" color="var(--text-3)" />今日摄入</p>
      <p class="nm">{{ dashboard.intakeToday }}<s>kcal</s></p>
      <p class="sub" style="color: var(--text-3)">还可摄入 {{ dashboard.intakeRemain }}</p>
    </div>
  </div>

  <div class="card glass ring-row">
    <svg width="82" height="82" viewBox="0 0 82 82">
      <defs>
        <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#10b981" />
          <stop offset="1" stop-color="#34d399" />
        </linearGradient>
      </defs>
      <circle cx="41" cy="41" :r="R" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="8" />
      <circle cx="41" cy="41" :r="R" fill="none" stroke="url(#ringGrad)" stroke-width="8" stroke-linecap="round"
        :stroke-dasharray="circ" :stroke-dashoffset="dashOffset" transform="rotate(-90 41 41)" />
      <text x="41" y="38" text-anchor="middle" font-size="18" font-weight="500" fill="#f4f6f8">{{ dashboard.workoutDone }}/{{ dashboard.workoutPlanned }}</text>
      <text x="41" y="53" text-anchor="middle" font-size="9" fill="#7d8593">本周训练</text>
    </svg>
    <div>
      <p class="ring-title">完成率 {{ rate }}%</p>
      <p class="ring-sub">已完成周一、周三训练<br />周五力量训练待打卡</p>
    </div>
  </div>

  <div class="card glass">
    <div class="card-head"><span>体重趋势</span><span class="muted">近 7 天</span></div>
    <TrendChart :data="dashboard.weightTrend" />
    <div class="axis">
      <span v-for="d in dashboard.weightTrend.filter((_, i) => i % 2 === 0)" :key="d.date">{{ d.date }}</span>
    </div>
  </div>

  <div class="card tip">
    <span class="tip-ic"><Icon name="star" :size="16" color="var(--on-brand)" :width="2.2" /></span>
    <div>
      <p class="tip-label">AI 今日建议</p>
      <p class="tip-text">{{ dashboard.aiTip }}</p>
    </div>
  </div>
</template>

<style scoped>
.hd { display: flex; justify-content: space-between; align-items: center; padding: 8px 0 18px; }
.hd h1 { font-size: 21px; font-weight: 500; letter-spacing: -0.02em; }
.hd p { font-size: 12px; color: var(--text-3); margin-top: 3px; }
.av { width: 40px; height: 40px; border-radius: 50%; background: var(--brand-grad); color: var(--on-brand); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 11px; margin-bottom: 12px; }
.mc { padding: 15px; }
.lb { font-size: 12px; color: var(--text-3); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.nm { font-size: 27px; font-weight: 500; letter-spacing: -0.02em; line-height: 1; }
.nm s { font-size: 13px; font-weight: 400; text-decoration: none; color: var(--text-3); }
.sub { font-size: 11px; margin-top: 8px; }
.card { padding: 15px; margin-bottom: 12px; }
.ring-row { display: flex; align-items: center; gap: 16px; }
.ring-title { font-size: 14px; font-weight: 500; }
.ring-sub { margin-top: 7px; font-size: 12px; color: var(--text-3); line-height: 1.5; }
.card-head { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 13px; font-weight: 500; }
.muted { color: var(--text-4); font-weight: 400; font-size: 11px; }
.axis { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-4); margin-top: 6px; }
.tip { background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.22); display: flex; gap: 12px; }
.tip-ic { width: 32px; height: 32px; border-radius: 10px; background: var(--brand-grad); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tip-label { font-size: 12px; color: var(--brand-bright); }
.tip-text { margin-top: 5px; font-size: 13px; line-height: 1.5; color: var(--text-2); }
</style>
