<template>
  <button
    @click="$emit('click')"
    class="group relative flex flex-col items-center justify-center gap-3 p-6 rounded-2xl glass cursor-pointer select-none opacity-0 animate-fade-in-up transition-all duration-300 hover:scale-105 hover:border-ns-accent/40 hover:shadow-xl hover:shadow-ns-accent/10 active:scale-[0.97]"
    :class="[`stagger-${number}`]"
  >
    <!-- Number Badge -->
    <span class="absolute top-3 left-3 w-7 h-7 flex items-center justify-center rounded-lg bg-ns-accent/15 text-ns-accent-light text-xs font-bold group-hover:bg-ns-accent/30 transition-colors duration-300">
      {{ number }}
    </span>

    <!-- Icon -->
    <div
      class="w-14 h-14 flex items-center justify-center rounded-xl transition-all duration-300 group-hover:scale-110"
      :class="iconBgClass"
    >
      <component :is="iconComponent" class="w-7 h-7 text-white" />
    </div>

    <!-- Label -->
    <span class="text-sm font-medium text-slate-300 group-hover:text-white transition-colors duration-300 text-center leading-tight">
      {{ label }}
    </span>

    <!-- Hover Glow -->
    <div class="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
      :style="{ boxShadow: `inset 0 0 30px ${glowColor}` }"
    ></div>
  </button>
</template>

<script setup>
import { computed, h } from 'vue'

const props = defineProps({
  number: { type: Number, required: true },
  label: { type: String, required: true },
  color: { type: String, default: 'indigo' },
  icon: { type: String, default: 'cog' },
})

defineEmits(['click'])

const colorMap = {
  indigo: { bg: 'bg-gradient-to-br from-indigo-500 to-indigo-700', glow: 'rgba(99,102,241,0.08)' },
  emerald: { bg: 'bg-gradient-to-br from-emerald-500 to-emerald-700', glow: 'rgba(16,185,129,0.08)' },
  amber: { bg: 'bg-gradient-to-br from-amber-500 to-amber-700', glow: 'rgba(245,158,11,0.08)' },
  rose: { bg: 'bg-gradient-to-br from-rose-500 to-rose-700', glow: 'rgba(244,63,94,0.08)' },
  cyan: { bg: 'bg-gradient-to-br from-cyan-500 to-cyan-700', glow: 'rgba(6,182,212,0.08)' },
  violet: { bg: 'bg-gradient-to-br from-violet-500 to-violet-700', glow: 'rgba(139,92,246,0.08)' },
  sky: { bg: 'bg-gradient-to-br from-sky-500 to-sky-700', glow: 'rgba(14,165,233,0.08)' },
  orange: { bg: 'bg-gradient-to-br from-orange-500 to-orange-700', glow: 'rgba(249,115,22,0.08)' },
}

const iconBgClass = computed(() => colorMap[props.color]?.bg || colorMap.indigo.bg)
const glowColor = computed(() => colorMap[props.color]?.glow || colorMap.indigo.glow)

// Simple SVG icon components
const icons = {
  users: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' })
  ]),
  chart: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
  ]),
  folder: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' })
  ]),
  calendar: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' })
  ]),
  chat: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' })
  ]),
  shield: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' })
  ]),
  cog: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }),
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' })
  ]),
  clipboard: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-7 h-7' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' })
  ]),
}

const iconComponent = computed(() => icons[props.icon] || icons.cog)
</script>
