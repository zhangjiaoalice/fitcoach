<script setup>
// 手机外壳：顶部灵动条 + 内容区（router-view）+ 底部 tabbar。
// 所有页面共用这个外壳，路由切换只换中间内容。
import { useRoute, useRouter } from 'vue-router'
import Icon from './Icon.vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { name: 'dashboard', label: '首页', icon: 'home' },
  { name: 'chat', label: '教练', icon: 'chat' },
  { name: 'diet', label: '记录', icon: 'record' },
  { name: 'me', label: '我的', icon: 'user' },
]
</script>

<template>
  <div class="wrap">
    <div class="screen">
      <div class="notch"><i /></div>
      <div class="content">
        <router-view />
      </div>
      <nav class="tabbar">
        <button
          v-for="t in tabs"
          :key="t.name"
          class="tab"
          :class="{ on: route.name === t.name }"
          @click="router.push({ name: t.name })"
        >
          <Icon :name="t.icon" :size="21" />
          <span>{{ t.label }}</span>
        </button>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  max-width: 420px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  align-items: stretch;
}
.screen {
  flex: 1;
  background: var(--bg-app);
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.notch {
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}
.notch i {
  width: 56px;
  height: 5px;
  border-radius: 3px;
  background: #242b36;
}
.content {
  flex: 1;
  overflow-y: auto;
  padding: 2px 18px 84px;
}
.tabbar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  border-top: 1px solid #171d26;
  background: rgba(12, 15, 20, 0.92);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: 8px;
}
.tab {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-4);
}
.tab.on {
  color: var(--brand);
}
</style>
