<script setup lang="ts">
import { computed } from 'vue'
import type { MarketMonthlyChangeByCounty } from '@/api/types'
import { MAIN_TYPE_FLAT, MAIN_TYPE_HOUSE } from '@/composables/useCountyMarket'
import CountyTrendChart from './CountyTrendChart.vue'

const props = defineProps<{
  house: MarketMonthlyChangeByCounty[]
  flat: MarketMonthlyChangeByCounty[]
}>()

/** Below this a "trend" is just a couple of bars - not enough to read a
 *  direction from, and the first month carries no change at all. */
const MIN_TREND_MONTHS = 3

/** Months the county has data for, across both property types. The two series
 *  usually cover the same months, but a type can be missing from an early one. */
const monthCount = computed(
  () => new Set([...props.house, ...props.flat].map((row) => row.month_start)).size,
)

/** Also covers the fail-soft case: a dead feed leaves both series empty, and an
 *  empty panel is worse than no panel. */
const hasEnoughHistory = computed(() => monthCount.value >= MIN_TREND_MONTHS)
</script>

<template>
  <section v-if="hasEnoughHistory" class="panel" aria-live="polite">
    <header class="panel-head">
      <h2>Ártrend</h2>
      <p class="total">az elmúlt 12 hónap · átlag Ft/m²</p>
    </header>

    <div class="charts">
      <CountyTrendChart :title="MAIN_TYPE_HOUSE" :rows="house" />
      <CountyTrendChart :title="MAIN_TYPE_FLAT" :rows="flat" />
    </div>
  </section>
</template>

<style scoped>
.panel {
  margin-top: 2rem;
}

.panel-head {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.5rem;
}

.total {
  margin: 0;
  color: #6b6b6b;
}

/* Two charts of 13 bars each. Side by side only once there is real room. */
.charts {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 62rem) {
  .charts {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
