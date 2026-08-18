<script setup lang="ts">
import { computed } from 'vue'
import type { MarketMonthlyByCity } from '@/api/types'
import type { County } from '@/data/counties'
import { formatCount } from '@/utils/formatMarket'
import MarketCards from './MarketCards.vue'

const props = defineProps<{
  city: string
  county: County
  rows: MarketMonthlyByCity[]
}>()

const total = computed(() => props.rows.reduce((sum, row) => sum + row.listing_count, 0))
</script>

<template>
  <section class="panel" aria-live="polite">
    <header class="panel-head">
      <h2>{{ city }} <span class="scope">({{ county.label }} megye)</span></h2>
      <p class="total">{{ formatCount(total) }} hirdetés</p>
    </header>

    <p v-if="rows.length === 0" class="hint">Ehhez a városhoz nincs adat erre a hónapra.</p>

    <MarketCards v-else :rows="rows" />
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

.scope {
  font-weight: 400;
  font-size: 1rem;
  color: #6b6b6b;
}

.total {
  margin: 0;
  color: #6b6b6b;
}
</style>
