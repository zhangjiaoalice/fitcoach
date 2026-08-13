<script setup>
// 体重趋势面积图。传入 [{date, v}]，自动归一化算出SVG 折线点。
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, required: true },
})

const W = 320
const H = 98
const padTop = 22
const padBottom = 26

const geom = computed(() => {
  const vals = props.data.map((d) => d.v)
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const range = max - min || 1
  const step = (W - 24) / (props.data.length - 1)
  const pts = props.data.map((d, i) => {
    const x = 12 + i * step
    const y = padTop + (1 - (d.v - min) / range) * (H - padTop - padBottom)
    return [Math.round(x), Math.round(y)]
  })
  const line = pts.map((p) => p.join(',')).join(' ')
  const area = `12,${H - padBottom} ${line} ${pts[pts.length - 1][0]},${H - padBottom}`
  return { line, area, last: pts[pts.length - 1] }
})
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" width="100%" :height="H" preserveAspectRatio="none">
    <defs>
      <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#10b981" stop-opacity=".35" />
        <stop offset="1" stop-color="#10b981" stop-opacity="0" />
      </linearGradient>
    </defs>
    <polyline :points="geom.area" fill="url(#areaGrad)" stroke="none" />
    <polyline :points="geom.line" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
    <circle :cx="geom.last[0]" :cy="geom.last[1]" r="4.5" fill="#0c0f14" stroke="#10b981" stroke-width="2.5" />
  </svg>
</template>
