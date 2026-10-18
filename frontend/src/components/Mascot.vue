<script setup lang="ts">
import { computed } from "vue";

interface Props {
  type?: "momo" | "hero";
  variant?: "avatar" | "full";
  size?: number;
}

const props = withDefaults(defineProps<Props>(), {
  type: "momo",
  variant: "full",
  size: 200,
});

const src = computed(
  () =>
    `/mascots/${props.type}${props.variant === "avatar" ? "-avatar" : ""}.png`
);

const actualSize = computed(() =>
  props.size > 0 ? props.size : props.variant === "avatar" ? 44 : 200
);

const alt = computed(
  () => `${props.type === "momo" ? "Fit Momo 女教练" : "Fit Hero 男教练"}`
);
</script>

<template>
  <img
    :src="src"
    :alt="alt"
    class="mascot"
    :class="variant"
    :style="{
      width: `${actualSize}px`,
      height: variant === 'avatar' ? `${actualSize}px` : 'auto',
    }"
  />
</template>

<style scoped>
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
    

