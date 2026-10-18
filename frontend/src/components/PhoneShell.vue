<script lang="ts">
// 显式默认导出，确保 `import PhoneShell from "./PhoneShell.vue"` 在类型检查/构建时始终可用。
export default {
  name: "PhoneShell",
};
</script>

<script setup lang="ts">
// 手机外壳：顶部灵动条 + 内容区（router-view）+ 底部 tabbar。
// 二级页面（如 /chat）通过 route.meta.hideTabbar 隐藏底部导航。
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icon from "./Icon.vue";

interface Tab {
  name: string;
  label: string;
  icon: string;
}

const route = useRoute();
const router = useRouter();

// 教练不再作为一级 tab，从此处去掉
const tabs: Tab[] = [
  { name: "dashboard", label: "首页", icon: "home" },
  { name: "diet", label: "记录", icon: "record" },
  { name: "me", label: "我的", icon: "user" },
];

const showTabbar = computed(() => !route.meta?.hideTabbar);
</script>

<template>
  <div class="wrap">
    <div class="screen">
      <div class="notch"><i /></div>
      <div class="content" :class="{ 'no-tabbar': !showTabbar }">
        <router-view />
      </div>
      <nav v-if="showTabbar" class="tabbar">
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
  overflow-y: auto;
  height: 100vh;
  padding: 2px 18px 84px;
  /* 隐藏滚动条：Firefox */
  scrollbar-width: none;
  /* 隐藏滚动条：IE/老 Edge */
  -ms-overflow-style: none;
}
/* 隐藏滚动条：Chrome / Safari / 新 Edge 等 Webkit 内核 */
.content::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
/* 无 tabbar 页面（如 /chat）不留底部 padding */
.content.no-tabbar {
  padding: 2px 18px 0;
}
.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  border-top: 1px solid var(--glass-border);
  background: var(--brand-light);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: 8px;
  z-index: 10;
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
