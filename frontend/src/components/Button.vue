<template>
  <button
    class="custom-btn relative text-white min-w-14 h-* rounded flex items-center justify-center overflow-hidden p-3"
    :style="{ backgroundColor: resolvedColor }"
    :title="tooltip || ''"
  >
    <span class="relative flex items-center gap-2">
      <slot />
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  color: {
    type: String,
    default: 'gray'  // fallback to gray if not provided
  },
  tooltip: {
    type: String,
    default: ''
  }
})

const colorMap = {
  gray:   '#6b7280', 
  red:    '#ff1a1a',
  green:  '#00cc44', 
  blue:   '#3b82f6', 
  yellow: '#f59e0b', 
  purple: '#7e22ce'  
}

const resolvedColor = computed(() => {
  return colorMap[props.color] || props.color
})
</script>

<style scoped>

.custom-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0);
}

.custom-btn:hover::before {
  background-color: rgba(0, 0, 0, 0.15);
}

.custom-btn > * {
  position: relative;
}
</style>
