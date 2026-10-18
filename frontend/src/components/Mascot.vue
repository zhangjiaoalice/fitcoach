<script setup lang="ts">
/**
 * 吉祥物组件
 *   - 优先加载 WebP（体积小 70-90%），PNG 作为兼容兜底
 *   - 登录页主视觉 full 版可通过 priority 开启 fetchpriority=high
 *   - 加 width/height 属性避免 CLS 布局偏移
 */
import { computed } from "vue";

interface Props {
  type?: "momo" | "hero";
  variant?: "avatar" | "full";
  size?: number;
  /** 首屏关键图传 true，启用 eager + fetchpriority=high */
  priority?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: "momo",
  variant: "full",
  size: 200,
  priority: false,
});

const base = computed(
  () => `/mascots/${props.type}${props.variant === "avatar" ? "-avatar" : ""}`
);
const webpSrc = computed(() => `${base.value}.webp`);
const pngSrc = computed(() => `${base.value}.png`);

const actualSize = computed(() =>
  props.size > 0 ? props.size : props.variant === "avatar" ? 44 : 200
);

// 图像真实宽高比（和 public/mascots 下的实际尺寸对齐），避免布局抖动
const dims = computed(() => {
  if (props.variant === "avatar") return { w: actualSize.value, h: actualSize.value };
  // full 版比例约 2:3（600×900 / 848×894），按 size 当宽度算高度
  const ratio = props.type === "momo" ? 900 / 600 : 894 / 600;
  return { w: actualSize.value, h: Math.round(actualSize.value * ratio) };
});

const alt = computed(
  () => `${props.type === "momo" ? "Fit Momo 女教练" : "Fit Hero 男教练"}`
);
</script>

<template>
  <picture class="mascot-pic" :class="variant">
    <source :srcset="webpSrc" type="image/webp" />
    <img
      :src="pngSrc"
      :alt="alt"
      class="mascot"
      :class="variant"
      :width="dims.w"
      :height="dims.h"
      :loading="priority ? 'eager' : 'lazy'"
      :fetchpriority="priority ? 'high' : 'auto'"
      decoding="async"
      :style="{
        width: `${actualSize}px`,
        height: variant === 'avatar' ? `${actualSize}px` : 'auto',
      }"
    />
  </picture>
</template>

<style scoped>
.mascot-pic {
  display: inline-block;
  line-height: 0;
}
.mascot-pic.avatar {
  border-radius: 50%;
  overflow: hidden;
}
.mascot {
  display: block;
  object-fit: cover;
}
.mascot.avatar {
  border-radius: 50%;
  border: 2px solid var(--glass-border);
  background: var(--bg-elevated);
}
.mascot.full {
  object-fit: contain;
}
</style>
