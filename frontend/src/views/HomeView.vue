<script setup lang="ts">
import { computed, onMounted } from 'vue'
import HungaryMap from '@/components/HungaryMap.vue'
import CountyMarketPanel from '@/components/CountyMarketPanel.vue'
import { useCountyMarket } from '@/composables/useCountyMarket'
import { MAP_ATTRIBUTION } from '@/data/counties'

const {
  monthStart,
  loading,
  error,
  isEmpty,
  countiesWithData,
  selectedCode,
  selectedCounty,
  selectedRows,
  select,
  load,
} = useCountyMarket()

const monthLabel = computed(() =>
  new Intl.DateTimeFormat('hu-HU', { year: 'numeric', month: 'long' }).format(
    new Date(`${monthStart.value}T00:00:00`),
  ),
)

onMounted(load)
</script>

<template>
  <main class="home">
    <header class="intro">
      <h1>Ingatlanpiac megyénként</h1>
      <p>
        Válassz egy megyét a térképen, és nézd meg a piaci adatait –
        <strong>{{ monthLabel }}</strong>
      </p>
    </header>

    <p v-if="error" class="notice notice-error" role="alert">{{ error }}</p>
    <p v-else-if="loading" class="notice">Adatok betöltése…</p>
    <p v-else-if="isEmpty" class="notice">
      Erre a hónapra ({{ monthLabel }}) még nincs feldolgozott adat.
    </p>

    <div class="map-wrap" :class="{ 'is-dim': loading || isEmpty || !!error }">
      <HungaryMap :available="countiesWithData" :selected="selectedCode" @select="select" />
    </div>

    <p class="attribution">
      <a :href="MAP_ATTRIBUTION.href" target="_blank" rel="noopener noreferrer">geo-data-hungary</a>
    </p>

    <CountyMarketPanel :county="selectedCounty" :rows="selectedRows" />
  </main>
</template>

<style scoped>
.home {
  max-width: 68rem;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
}

.intro h1 {
  margin: 0 0 0.35rem;
  font-size: 1.9rem;
}

.intro p {
  margin: 0;
  color: #6b6b6b;
}

.notice {
  margin: 1.25rem 0 0;
  padding: 0.7rem 1rem;
  border-radius: 0.4rem;
  background: #f5f2ee;
  color: #6b6b6b;
}

.notice-error {
  background: #fdeceb;
  color: #b42318;
}

.map-wrap {
  margin: 1rem 0 0.25rem;
  transition: opacity 150ms ease-out;
}

.map-wrap.is-dim {
  opacity: 0.45;
}

.attribution {
  margin: 0 0 1.75rem;
  text-align: right;
  font-size: 0.75rem;
  color: #9a9a9a;
}

.attribution a {
  color: inherit;
}
</style>
