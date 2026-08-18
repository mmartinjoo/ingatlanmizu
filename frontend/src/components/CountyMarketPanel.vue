<script setup lang="ts">
import { computed } from 'vue'
import type { MarketMonthlyByCounty } from '@/api/types'
import type { County } from '@/data/counties'

const props = defineProps<{
  county: County | null
  rows: MarketMonthlyByCounty[]
}>()

const huf = new Intl.NumberFormat('hu-HU', { maximumFractionDigits: 0 })
const percent = new Intl.NumberFormat('hu-HU', { maximumFractionDigits: 1 })

function formatHuf(value: number | null): string {
  return value === null ? '–' : `${huf.format(value)} Ft`
}

function formatRatio(value: number | null): string {
  return value === null ? '–' : `${percent.format(value)}%`
}

function formatCount(value: number | null): string {
  return value === null ? '–' : huf.format(value)
}

const total = computed(() => props.rows.reduce((sum, row) => sum + row.listing_count, 0))
</script>

<template>
  <section class="panel" aria-live="polite">
    <p v-if="!county" class="hint">Válassz egy megyét a térképen a piaci adatok megtekintéséhez.</p>

    <template v-else>
      <header class="panel-head">
        <h2>{{ county.label }}</h2>
        <p class="total">{{ formatCount(total) }} hirdetés</p>
      </header>

      <p v-if="rows.length === 0" class="hint">Ehhez a megyéhez nincs adat erre a hónapra.</p>

      <div v-else class="cards">
        <article v-for="row in rows" :key="row.main_type" class="card">
          <h3>{{ row.main_type }}</h3>
          <dl>
            <div>
              <dt>Hirdetések száma</dt>
              <dd>{{ formatCount(row.listing_count) }}</dd>
            </div>
            <div>
              <dt>Medián négyzetméterár</dt>
              <dd class="highlight">{{ formatHuf(row.median_price_per_sqm) }}</dd>
            </div>
            <div>
              <dt>Újépítés aránya</dt>
              <dd>{{ formatRatio(row.new_build_ratio) }}</dd>
            </div>
            <div>
              <dt>Medián építési év</dt>
              <dd>{{ row.median_year_of_building || '–' }}</dd>
            </div>
            <div>
              <dt>Medián állapot (1–5)</dt>
              <dd>{{ row.median_condition_score ?? '–' }}</dd>
            </div>
          </dl>

          <p class="split">
            <span>Új: {{ formatCount(row.new_build_count) }}</span>
            <span>Régi: {{ formatCount(row.old_build_count) }}</span>
            <span>Ismeretlen: {{ formatCount(row.unknown_build_count) }}</span>
          </p>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.panel {
  min-height: 8rem;
}

.hint {
  color: #6b6b6b;
  margin: 0;
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

dd.highlight {
  color: #e8590c;
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
