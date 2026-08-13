<script setup>
import { profile } from '../api/mock.js'
import Icon from '../components/Icon.vue'

const items = [
  { icon: 'user', label: '个人画像', desc: '身高体重、目标、饮食偏好' },
  { icon: 'record', label: '计划中心', desc: '查看与调整每周计划' },
  { icon: 'doc', label: '健身知识库', desc: 'RAG 知识问答来源' },
  { icon: 'spinner', label: 'Agent Trace', desc: '工具调用与执行链路' },
]
</script>

<template>
  <header class="hd">
    <div>
      <h1>我的</h1>
      <p>减脂第 {{ profile.dayCount }} 天</p>
    </div>
    <div class="av">{{ profile.initials }}</div>
  </header>

  <div class="card glass" v-for="it in items" :key="it.label">
    <span class="mi"><Icon :name="it.icon" :size="18" color="var(--brand)" :width="1.8" /></span>
    <div class="tx">{{ it.label }}<small>{{ it.desc }}</small></div>
    <span class="arrow">›</span>
  </div>
</template>

<style scoped>
.hd { display: flex; justify-content: space-between; align-items: center; padding: 8px 0 18px; }
.hd h1 { font-size: 21px; font-weight: 500; letter-spacing: -0.02em; }
.hd p { font-size: 12px; color: var(--text-3); margin-top: 3px; }
.av { width: 40px; height: 40px; border-radius: 50%; background: var(--brand-grad); color: var(--on-brand); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; }
.card { display: flex; align-items: center; gap: 12px; padding: 14px 15px; margin-bottom: 10px; }
.mi { width: 36px; height: 36px; border-radius: 10px; background: rgba(16, 185, 129, 0.12); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tx { flex: 1; font-size: 13px; color: var(--text-1); }
.tx small { display: block; color: var(--text-4); font-size: 11px; margin-top: 2px; }
.arrow { color: var(--text-4); font-size: 18px; }
</style>
