<script setup lang="ts">
import { computed } from 'vue'
import type { MarketIndicatorsMonthly } from '@/api/types'
import { formatHuf, formatRate } from '@/utils/formatMarket'
import {
  LTV,
  REFERENCE_SIZE_SQM,
  TERM_YEARS,
  referenceMonthlyPayment,
  referencePrice,
} from '@/utils/mortgage'

/** Structural subset - satisfied by both county and city rows. */
interface PricedRow {
  main_type: string
  median_price_per_sqm: number
}

const props = defineProps<{
  /** What the figures describe: a city name, or the county. */
  scopeLabel: string
  rows: PricedRow[]
  indicators: MarketIndicatorsMonthly
}>()

const estimates = computed(() =>
  props.rows.map((row) => ({
    mainType: row.main_type,
    price: referencePrice(row.median_price_per_sqm),
    payment: referenceMonthlyPayment(row.median_price_per_sqm, props.indicators.median_apr),
  })),
)
</script>

<template>
  <section v-if="estimates.length > 0" class="affordability">
    <h2>
      {{ scopeLabel }}: mennyibe kerülne egy {{ REFERENCE_SIZE_SQM }} m²-es ingatlan?
    </h2>

    <ul class="rows">
      <li v-for="item in estimates" :key="item.mainType" class="row">
        <span class="type">{{ item.mainType }}</span>
        <span class="price">≈ {{ formatHuf(Math.round(item.price)) }}</span>
        <span class="arrow" aria-hidden="true">→</span>
        <span class="payment">≈ {{ formatHuf(Math.round(item.payment)) }} / hó</span>
      </li>
    </ul>

    <p class="assumptions">
      Becslés: {{ REFERENCE_SIZE_SQM }} m², {{ TERM_YEARS }} éves futamidő,
      {{ Math.round((1 - LTV) * 100) }}% -os önerő, a jelenlegi ÁTLAG
      {{ formatRate(indicators.median_apr) }}-os THM mellett. Nem ajánlat.
    </p>
  </section>
</template>

<style scoped>
.affordability {
  margin: 2.25rem 0 0;
  padding: 1.25rem 1.4rem;
  border: 1px solid #e5e0da;
  border-radius: 0.5rem;
  background: #fffaf5;
}

h2 {
  margin: 0 0 0.9rem;
  font-size: 1.15rem;
}

.rows {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.row {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  font-variant-numeric: tabular-nums;
}

.type {
  min-width: 4rem;
  font-weight: 600;
  color: #b4441f;
}

.price {
  color: #6b6b6b;
}

.arrow {
  color: #c9beb2;
}

.payment {
  font-weight: 700;
}

.assumptions {
  margin: 1rem 0 0;
  padding-top: 0.75rem;
  border-top: 1px solid #f0e6dc;
  font-size: 0.72rem;
  color: #9a9a9a;
}
</style>
