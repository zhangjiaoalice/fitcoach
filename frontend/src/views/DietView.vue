<script setup lang="ts">
import { computed } from "vue";
import { profile, dietLogs } from "../api/mock";
import Icon from "../components/Icon.vue";

const total = computed(() => dietLogs.reduce((s, d) => s + d.kcal, 0));

function analyze(): void {
  // 后端 M5 的 analyze_diet_log 工具就绪后，这里改成调用 /api/agent 触发分析
  alert("（示例）将调用 AI 分析今日摄入");
}
</script>

<template>
  <header class="hd">
    <div>
      <h1>饮食记录</h1>
      <p>8 月 4 日 · 已摄入 {{ total }} kcal</p>
    </div>
    <div class="av">{{ profile.initials }}</div>
  </header>

  <div class="card glass nl">
    <Icon name="mic" :size="17" color="var(--brand)" />
    <span>说一句“午餐吃了鸡胸肉和米饭”，自动结构化</span>
  </div>

  <div v-for="d in dietLogs" :key="d.id" class="li">
    <span class="mi"><Icon :name="d.icon" :size="18" :color="d.color" :width="1.8" /></span>
    <div class="tx">{{ d.name }}<small>{{ d.meal }} · {{ d.time }}</small></div>
    <span class="kc">{{ d.kcal }} kcal</span>
  </div>

  <button class="cta" @click="analyze">让 AI 分析今日摄入 ↗</button>
</template>

<style scoped>
.hd { display: flex; justify-content: space-between; align-items: center; padding: 8px 0 18px; }
.hd h1 { font-size: 21px; font-weight: 500; letter-spacing: -0.02em; }
.hd p { font-size: 12px; color: var(--text-3); margin-top: 3px; }
.av { width: 40px; height: 40px; border-radius: 50%; background: var(--brand-grad); color: var(--on-brand); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; }
.nl { display: flex; align-items: center; gap: 11px; padding: 13px 15px; margin-bottom: 4px; font-size: 13px; color: var(--text-3); }
.li { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--hairline); }
.mi { width: 36px; height: 36px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tx { flex: 1; font-size: 13px; color: var(--text-2); }
.tx small { display: block; color: var(--text-4); font-size: 11px; margin-top: 2px; }
.kc { font-size: 13px; color: var(--text-3); }
.cta { margin-top: 16px; }
</style>
