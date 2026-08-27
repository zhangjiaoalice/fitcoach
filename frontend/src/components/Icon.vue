<script setup lang="ts">
// 线性图标库。用法：<Icon name="home" :size="20" color="#10b981" />
// stroke 统一用 currentColor 或传入 color，风格一致。

interface Props {
  name: string;
  size?: number | string;
  color?: string;
  width?: number;
}

withDefaults(defineProps<Props>(), {
  size: 20,
  color: "currentColor",
  width: 2,
});

const paths: Record<string, string> = {
  check: '<path d="M20 6L9 17l-5-5"/>',
  spinner: '<circle cx="12" cy="12" r="9" opacity=".3"/><path d="M12 3a9 9 0 0 1 9 9"/>',
  doc: '<path d="M4 19V5a2 2 0 0 1 2-2h9l5 5v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M9 8h4M9 12h6M9 16h6"/>',
  warn: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 4L2 18a2 2 0 0 0 1.7 3h16.6a2 2 0 0 0 1.7-3L13.7 4a2 2 0 0 0-3.4 0z"/>',
  scale: '<path d="M12 3v18M5 8l7-5 7 5"/>',
  flame: '<path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7z"/>',
  star: '<path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7-6.3-4.6L5.7 21l2.3-7-6-4.6h7.6z"/>',
  mic: '<path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10a7 7 0 0 1-14 0M12 17v4"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  fork: '<path d="M4 3v18M4 9h8a4 4 0 0 0 0-8H4M16 3v18M20 3v7a4 4 0 0 1-4 4"/>',
  cup: '<path d="M6 2h12l-1 9a5 5 0 0 1-10 0z"/><path d="M6 11h12M12 16v6"/>',
  fish: '<path d="M3 12c4-6 14-6 18 0-4 6-14 6-18 0z"/><circle cx="9" cy="12" r="1.3"/>',
  home: '<path d="M3 11l9-8 9 8M5 10v10h14V10"/>',
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  record: '<path d="M9 11l3 3 8-8M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
};
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    :stroke="color"
    :stroke-width="width"
    stroke-linecap="round"
    stroke-linejoin="round"
    v-html="paths[name] || ''"
  />
</template>
