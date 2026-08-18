<script setup lang="ts">
import { computed } from 'vue'
import { COUNTIES, MAP_VIEW_BOX, type County } from '@/data/counties'

const props = defineProps<{
  /** KSH codes that have data this month. Everything else renders as disabled. */
  available: Set<number>
  selected: number | null
}>()

const emit = defineEmits<{ select: [kshCode: number] }>()

/** Rough advance width of one character, as a fraction of the font size. */
const CHAR_WIDTH = 0.52
const MIN_FONT = 46
const MAX_FONT = 92

/** Break long names at hyphens, which is where Hungarian county names divide. */
function wrap(label: string): string[] {
  if (label.length <= 12) return [label]

  const parts = label.split('-')
  if (parts.length === 1) return [label]

  // Greedily pack segments into two roughly equal lines.
  const target = label.length / 2
  const lines: string[] = []
  let current = ''
  for (const [index, part] of parts.entries()) {
    const isLast = index === parts.length - 1
    const candidate = current ? `${current}-${part}` : part
    if (current && candidate.length > target && !isLast) {
      lines.push(`${current}-`)
      current = part
    } else if (current && candidate.length > target * 1.5) {
      lines.push(`${current}-`)
      current = part
    } else {
      current = candidate
    }
  }
  if (current) lines.push(current)
  return lines
}

interface RenderedCounty {
  county: County
  lines: string[]
  fontSize: number
  hasData: boolean
  isSelected: boolean
}

const rendered = computed<RenderedCounty[]>(() =>
  COUNTIES.map((county) => {
    const lines = wrap(county.label)
    const longest = Math.max(...lines.map((line) => line.length))
    // Fit the widest line inside the shape's clearance circle.
    const fitted = (county.labelRadius * 1.85) / (longest * CHAR_WIDTH)
    return {
      county,
      lines,
      fontSize: Math.round(Math.min(MAX_FONT, Math.max(MIN_FONT, fitted))),
      hasData: props.available.has(county.kshCode),
      isSelected: props.selected === county.kshCode,
    }
  }),
)

function onActivate(item: RenderedCounty) {
  if (!item.hasData) return
  emit('select', item.county.kshCode)
}
</script>

<template>
  <svg
    class="map"
    :viewBox="MAP_VIEW_BOX"
    role="group"
    aria-label="Magyarország megyéi"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g
      v-for="item in rendered"
      :key="item.county.kshCode"
      class="county"
      :class="{ 'is-selected': item.isSelected, 'is-empty': !item.hasData }"
    >
      <path
        :d="item.county.d"
        :tabindex="item.hasData ? 0 : undefined"
        :role="item.hasData ? 'button' : undefined"
        :aria-pressed="item.hasData ? item.isSelected : undefined"
        :aria-label="
          item.hasData
            ? item.county.label
            : `${item.county.label} – nincs adat erre a hónapra`
        "
        @click="onActivate(item)"
        @keydown.enter.prevent="onActivate(item)"
        @keydown.space.prevent="onActivate(item)"
      />
      <text
        :x="item.county.labelX"
        :y="item.county.labelY"
        :font-size="item.fontSize"
        text-anchor="middle"
        :dy="(-(item.lines.length - 1) * item.fontSize * 1.05) / 2 + item.fontSize * 0.34"
      >
        <tspan
          v-for="(line, index) in item.lines"
          :key="line"
          :x="item.county.labelX"
          :dy="index === 0 ? 0 : item.fontSize * 1.05"
          >{{ line }}</tspan
        >
      </text>
    </g>
  </svg>
</template>

<style scoped>
.map {
  display: block;
  width: 100%;
  height: auto;
}

.county path {
  fill: var(--county-fill, #fde7c3);
  fill-rule: evenodd; /* Keeps Budapest cut out of Pest. Do not remove. */
  stroke: #b4441f;
  stroke-width: 4;
  stroke-linejoin: round;
  cursor: pointer;
  transition:
    fill 120ms ease-out,
    filter 120ms ease-out;
}

.county text {
  fill: #3f2d20;
  pointer-events: none; /* Never swallow a click meant for the path. */
  font-family: inherit;
  font-weight: 600;
  user-select: none;
}

.county path:hover {
  fill: #f9b169;
}

.county path:focus-visible {
  outline: none;
  stroke: #1c1917;
  stroke-width: 12;
}

.county.is-selected path {
  fill: #e8590c;
}

.county.is-selected text {
  fill: #fff;
}

.county.is-empty path {
  fill: #ececec;
  stroke: #c9c9c9;
  cursor: default;
  pointer-events: none; /* Not clickable, and it looks it. */
}

.county.is-empty text {
  fill: #a3a3a3;
}
</style>
