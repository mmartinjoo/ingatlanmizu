<script setup lang="ts">
import { computed } from 'vue'
import type { MarketMonthlyByCounty } from '@/api/types'
import type { County } from '@/data/counties'
import { formatCount } from '@/utils/formatMarket'
import MarketCards from './MarketCards.vue'

const props = defineProps<{
  county: County | null
  rows: MarketMonthlyByCounty[]
}>()

const total = computed(() => props.rows.reduce((sum, row) => sum + row.listing_count, 0))

/** Budapest is the capital, not a megye - "Budapest megyei" would be wrong. */
const heading = computed(() => {
  if (!props.county) return ''
  return props.county.dbName === 'Budapest'
    ? 'Budapesti ingatlanhirdetések'
    : `${props.county.label} megyei ingatlanhirdetések`
})
</script>

<template>
  <section class="panel" aria-live="polite">
    <p v-if="!county" class="hint">Válassz egy megyét a térképen a piaci adatok megtekintéséhez.</p>

    <template v-else>
      <header class="panel-head">
        <h2>{{ heading }}</h2>
        <p class="total">{{ formatCount(total) }} hirdetés</p>
      </header>

      <p v-if="rows.length === 0" class="hint">Ehhez a megyéhez nincs adat erre a hónapra.</p>

      <MarketCards v-else :rows="rows" />
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
</style>
