<script setup lang="ts">
import { computed, onMounted } from 'vue'
import HungaryMap from '@/components/HungaryMap.vue'
import MonthPicker from '@/components/MonthPicker.vue'
import CountyMarketPanel from '@/components/CountyMarketPanel.vue'
import CityPicker from '@/components/CityPicker.vue'
import CountyTrendPanel from '@/components/CountyTrendPanel.vue'
import CityMarketPanel from '@/components/CityMarketPanel.vue'
import MarketIndicators from '@/components/MarketIndicators.vue'
import AffordabilityPanel from '@/components/AffordabilityPanel.vue'
import { useCountyMarket } from '@/composables/useCountyMarket'
import { formatMonth } from '@/utils/formatMonth'
import { MAP_ATTRIBUTION } from '@/data/counties'

const {
  months,
  monthStart,
  loading,
  error,
  isEmpty,
  countiesWithData,
  selectedCode,
  selectedCounty,
  selectedRows,
  select,
  selectMonth,
  load,
  cities,
  selectedCity,
  cityRows,
  selectCity,
  indicators,
  trendHouse,
  trendFlat,
  listingCount,
} = useCountyMarket()

const monthLabel = computed(() => formatMonth(monthStart.value))

/** Affordability follows whatever scope the page is showing: city if one is
 *  picked, otherwise the county. */
const affordabilityScope = computed(() => {
  if (!selectedCounty.value) return null
  if (selectedCity.value) {
    return { label: selectedCity.value, rows: cityRows.value }
  }
  return { label: selectedCounty.value.dbName, rows: selectedRows.value }
})

onMounted(load)
</script>

<template>
  <main class="home">
    <header class="intro">
      <h1 v-if="listingCount">Ingatlanpiac alakulása {{ listingCount }} hirdetés alapján</h1>
      <h1 v-else>Ingatlanpiac alakulása</h1>
      <p>
        Válassz egy megyét a térképen, és nézd meg a piaci adatokat –
        <strong>{{ monthLabel }}</strong>
      </p>
    </header>    

    <p v-if="error" class="notice notice-error" role="alert">{{ error }}</p>
    <p v-else-if="loading" class="notice">Adatok betöltése…</p>
    <p v-else-if="isEmpty" class="notice">
      {{
        monthLabel
          ? `Erre a hónapra (${monthLabel}) még nincs feldolgozott adat.`
          : 'Még nincs feldolgozott adat.'
      }}
    </p>

    <MarketIndicators v-if="indicators" :indicators="indicators" />

    <div class="map-wrap" :class="{ 'is-dim': loading || isEmpty || !!error }">
      <HungaryMap :available="countiesWithData" :selected="selectedCode" @select="select" />
    </div>    

    <MonthPicker :months="months" :selected="monthStart" @select="selectMonth" />

    <CountyMarketPanel :county="selectedCounty" :rows="selectedRows" />

    <template v-if="selectedCounty && countiesWithData.has(selectedCounty.kshCode)">
      <CountyTrendPanel :house="trendHouse" :flat="trendFlat" />

      <CityPicker :cities="cities" :selected="selectedCity" :county="selectedCounty.dbName" @select="selectCity" />
      <CityMarketPanel
        v-if="selectedCity"
        :city="selectedCity"
        :county="selectedCounty"
        :rows="cityRows"
      />
    </template>

    <AffordabilityPanel
      v-if="affordabilityScope && indicators && affordabilityScope.rows.length > 0"
      :scope-label="affordabilityScope.label"
      :rows="affordabilityScope.rows"
      :indicators="indicators"
    />

    <footer class="attribution">
      Megyehatárok:
      <a :href="MAP_ATTRIBUTION.href" target="_blank" rel="noopener noreferrer">geo-data-hungary</a>
      ·
      <a :href="MAP_ATTRIBUTION.licenseHref" target="_blank" rel="noopener noreferrer"
        >CC BY-SA 3.0</a
      >
    </footer>
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
  margin: 1rem 0 1.25rem;
  transition: opacity 150ms ease-out;
}

.map-wrap.is-dim {
  opacity: 0.45;
}

.attribution {
  margin: 3rem 0 0;
  padding-top: 1rem;
  border-top: 1px solid #ece7e1;
  font-size: 0.75rem;
  color: #9a9a9a;
}

.attribution a {
  color: inherit;
}
</style>
