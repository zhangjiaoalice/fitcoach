<script setup>
import { profile, chatThread } from '../api/mock.js'
import Icon from '../components/Icon.vue'
</script>

<template>
  <header class="hd">
    <div>
      <h1>AI 教练</h1>
      <p>已读取画像 · 减脂第 {{ profile.dayCount }} 天</p>
    </div>
    <div class="av">{{ profile.initials }}</div>
  </header>

  <template v-for="(m, i) in chatThread" :key="i">
    <div v-if="m.type === 'user'" class="bub bu">{{ m.text }}</div>

    <div v-else-if="m.type === 'tool'" class="tool glass">
      <span class="ic" :class="m.tone">
        <Icon v-if="m.tone === 'brand'" name="check" :size="14" color="var(--brand)" :width="2.4" />
        <Icon v-else name="spinner" :size="14" color="var(--info)" :width="2.2" />
      </span>
      {{ m.label }}
      <span class="st" :style="{ color: m.tone === 'brand' ? 'var(--brand-bright)' : 'var(--info)' }">{{ m.status }}</span>
    </div>

    <div v-else-if="m.type === 'citation'" class="tool glass">
      <span class="ic gray"><Icon name="doc" :size="14" color="var(--text-3)" :width="2" /></span>
      {{ m.label }}
    </div>

    <div v-else-if="m.type === 'assistant'" class="bub ba">
      {{ m.text }}
      <div v-if="m.plan" class="pcard">
        <div class="prow-head">
          <span>本周计划草稿</span>
          <span class="goal">{{ m.plan.goal }}</span>
        </div>
        <div v-for="(r, ri) in m.plan.rows" :key="ri" class="prow">
          <span class="day">{{ r.day }}</span>{{ r.title }}<span class="tag">{{ r.tag }}</span>
        </div>
        <button class="cta">保存为当前计划</button>
      </div>
    </div>

    <div v-else-if="m.type === 'risk'" class="tool risk">
      <span class="ic warn"><Icon name="warn" :size="14" color="var(--warn)" :width="2.2" /></span>
      <span style="color: var(--warn)">{{ m.text }}</span>
    </div>
  </template>
</template>

<style scoped>
.hd { display: flex; justify-content: space-between; align-items: center; padding: 8px 0 18px; }
.hd h1 { font-size: 21px; font-weight: 500; letter-spacing: -0.02em; }
.hd p { font-size: 12px; color: var(--text-3); margin-top: 3px; }
.av { width: 40px; height: 40px; border-radius: 50%; background: var(--brand-grad); color: var(--on-brand); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; }
.bub { max-width: 82%; padding: 11px 14px; font-size: 13px; line-height: 1.55; margin-bottom: 10px; border-radius: 16px; }
.bu { background: var(--brand-grad); color: var(--on-brand); margin-left: auto; border-bottom-right-radius: 5px; }
.ba { color: var(--text-2); }
.tool { display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 8px; font-size: 12px; color: var(--text-2); }
.tool .ic { width: 26px; height: 26px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ic.brand { background: rgba(16, 185, 129, 0.14); }
.ic:not(.brand):not(.gray):not(.warn) { background: rgba(56, 138, 221, 0.16); }
.ic.gray { background: rgba(255, 255, 255, 0.06); }
.ic.warn { background: rgba(234, 179, 8, 0.18); }
.tool .st { margin-left: auto; font-size: 11px; }
.risk { background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.25); border-radius: 12px; }
.pcard { border: 1px solid rgba(16, 185, 129, 0.28); border-radius: 14px; padding: 13px; margin-top: 8px; background: rgba(16, 185, 129, 0.06); }
.prow-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: var(--text-1); }
.goal { font-size: 11px; color: var(--brand-bright); font-weight: 400; }
.prow { display: flex; align-items: center; gap: 9px; padding: 7px 0; font-size: 12px; color: var(--text-2); border-bottom: 1px solid var(--hairline); }
.prow:last-of-type { border:0; }
.day { width: 30px; height: 23px; border-radius: 7px; background: rgba(16, 185, 129, 0.16); color: var(--brand-bright); display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0; }
.tag { margin-left: auto; color: var(--text-3); }
</style>
