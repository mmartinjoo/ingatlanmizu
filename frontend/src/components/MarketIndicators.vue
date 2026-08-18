<script setup lang="ts">
import { computed } from 'vue'
import type { MarketIndicatorsMonthly } from '@/api/types'
import { formatHuf, formatRate } from '@/utils/formatMarket'
import { LOAN_ASSUMPTION } from '@/utils/mortgage'

const props = defineProps<{
  indicators: MarketIndicatorsMonthly
}>()

interface Tile {
  key: string
  label: string
  value: string
  /** Present only for the two metrics that carry a min/max spread. */
  range?: {
    minLabel: string
    maxLabel: string
    /** Median position along the bar, 0-1. */
    offset: number
  }
}

/** Where the median sits between min and max. Clamped so a degenerate
 *  range (min === max) can't produce NaN or overflow the bar. */
function offsetOf(median: number, min: number, max: number): number {
  const span = max - min
  if (span <= 0) return 0.5
  return Math.min(1, Math.max(0, (median - min) / span))
}

const tiles = computed<Tile[]>(() => {
  const i = props.indicators
  return [
    { key: 'base_rate', label: 'Jegybanki alapkamat', value: formatRate(i.base_rate) },
    { key: 'inflation', label: 'Infláció', value: formatRate(i.inflation) },
    {
      key: 'apr',
      label: 'Átlag THM',
      value: formatRate(i.median_apr),
      range: {
        minLabel: formatRate(i.lowest_apr),
        maxLabel: formatRate(i.highest_apr),
        offset: offsetOf(i.median_apr, i.lowest_apr, i.highest_apr),
      },
    },
    {
      key: 'installment',
      label: 'Átlag havi törlesztő',
      value: formatHuf(Math.round(i.median_monthly_installment)),
      range: {
        minLabel: formatHuf(i.lowest_monthly_installment),
        maxLabel: formatHuf(i.highest_monthly_installment),
        offset: offsetOf(
          i.median_monthly_installment,
          i.lowest_monthly_installment,
          i.highest_monthly_installment,
        ),
      },
    },
  ]
})
</script>

<template>
  <section class="indicators" aria-label="Havi piaci mutatók">
    <div class="tiles">
      <article v-for="tile in tiles" :key="tile.key" class="tile" :data-key="tile.key">
        <p class="label">{{ tile.label }}</p>
        <p class="value">{{ tile.value }}</p>

        <div v-if="tile.range" class="range" :data-offset="tile.range.offset.toFixed(4)">
          <div class="track">
            <span class="marker" :style="{ left: `${tile.range.offset * 100}%` }" />
          </div>
          <p class="bounds">
            <span>{{ tile.range.minLabel }}</span>
            <span>{{ tile.range.maxLabel }}</span>
          </p>
        </div>
      </article>
    </div>

    <p class="footnote">
      Törlesztő: {{ LOAN_ASSUMPTION }} · Forrás: MNB, KSH, Bankmonitor
    </p>
  </section>
</template>

<style scoped>
.indicators {
  margin: 1.5rem 0 0;
}

/* Exactly four tiles, so auto-fit is the wrong tool - it lands on 3+1 at
   common widths. Explicit steps keep it 1 / 2x2 / 4-across. */
.tiles {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 30rem) {
  .tiles {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 62rem) {
  .tiles {
    grid-template-columns: repeat(4, 1fr);
  }
}

.tile {
  border: 1px solid #e5e0da;
  border-radius: 0.5rem;
  padding: 0.9rem 1.1rem;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.label {
  margin: 0 0 0.3rem;
  font-size: 0.8rem;
  color: #6b6b6b;
}

.value {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #b4441f;
}

.range {
  margin-top: 0.7rem;
}

.track {
  position: relative;
  height: 4px;
  border-radius: 2px;
  background: #f0e6dc;
}

.marker {
  position: absolute;
  top: 50%;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #e8590c;
  transform: translate(-50%, -50%);
}

.bounds {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin: 0.35rem 0 0;
  font-size: 0.7rem;
  color: #9a9a9a;
  font-variant-numeric: tabular-nums;
}

.footnote {
  margin: 0.75rem 0 0;
  font-size: 0.72rem;
  color: #9a9a9a;
}
</style>
