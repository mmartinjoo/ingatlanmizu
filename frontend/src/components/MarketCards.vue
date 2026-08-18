<script setup lang="ts">
import { formatConditionScore, formatCount, formatHuf, formatRatio } from '@/utils/formatMarket'

/** Structural subset shared by `MarketMonthlyByCounty` and `MarketMonthlyByCity` -
 *  everything the cards actually render. Either type satisfies this directly. */
interface MarketCardRow {
  main_type: string
  listing_count: number
  new_build_count: number
  old_build_count: number
  unknown_build_count: number
  median_price_per_sqm: number
  median_year_of_building: number
  median_condition_score: number
  new_build_ratio: number | null
}

defineProps<{
  rows: MarketCardRow[]
}>()
</script>

<template>
  <div class="cards">
    <article v-for="row in rows" :key="row.main_type" class="card">
      <h3>{{ row.main_type }}</h3>
      <dl>
        <div>
          <dt>Hirdetések száma</dt>
          <dd>{{ formatCount(row.listing_count) }}</dd>
        </div>
        <div>
          <dt>Átlagos négyzetméterár</dt>
          <dd>{{ formatHuf(row.median_price_per_sqm) }}</dd>
        </div>
        <div>
          <dt>Újépítésú ingatalnok aránya</dt>
          <dd>{{ formatRatio(row.new_build_ratio, '0%') }}</dd>
        </div>
        <div>
          <dt>Ingatlanok átlag kora</dt>
          <dd v-if="row.median_year_of_building">{{ new Date().getFullYear() - row.median_year_of_building }} év ({{ row.median_year_of_building }})</dd>
          <dd v-else>-</dd>
        </div>
        <div>
          <dt>Meghirdetett ingatlanok állapota</dt>
          <dd>{{ formatConditionScore(row.median_condition_score) }}</dd>
        </div>
      </dl>

      <p class="split">
        <span>Új építésű: {{ formatCount(row.new_build_count) }}</span>
        <span>Régebbi: {{ formatCount(row.old_build_count) }}</span>
        <span>Ismeretlen: {{ formatCount(row.unknown_build_count) }}</span>
      </p>
    </article>
  </div>
</template>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
  gap: 1rem;
}

.card {
  border: 1px solid #e5e0da;
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  background: #fff;
}

.card h3 {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
  color: #b4441f;
}

dl {
  margin: 0;
  display: grid;
  gap: 0.4rem;
}

dl > div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.9rem;
}

dt {
  color: #6b6b6b;
}

dd {
  margin: 0;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.split {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0.9rem 0 0;
  padding-top: 0.75rem;
  border-top: 1px solid #f0ece7;
  font-size: 0.8rem;
  color: #6b6b6b;
}
</style>
