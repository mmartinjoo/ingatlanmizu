import { computed, ref, shallowRef } from 'vue'
import {
  fetchCitiesForCounty,
  fetchMarketIndicatorsMonthly,
  fetchMarketMonthlyByCity,
  fetchMarketMonthlyByCounty,
  fetchMarketMonths,
} from '@/api/market'
import type {
  MarketIndicatorsMonthly,
  MarketMonthlyByCity,
  MarketMonthlyByCounty,
} from '@/api/types'
import { COUNTIES, type County } from '@/data/counties'

export function useCountyMarket() {
  const months = shallowRef<string[]>([])
  /** Empty until the API tells us which months exist. */
  const monthStart = ref('')
  const rows = shallowRef<MarketMonthlyByCounty[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedCode = ref<number | null>(null)

  /** Rows already fetched, keyed by month. Switching back is instant and silent. */
  const cache = new Map<string, MarketMonthlyByCounty[]>()

  /** Only the newest request may write to `rows`. Guards against fast switching. */
  let requestId = 0

  // --- City filter, scoped to whichever county is currently selected. ---

  const cities = shallowRef<string[]>([])
  const selectedCity = ref<string | null>(null)
  const cityRows = shallowRef<MarketMonthlyByCity[]>([])
  const cityLoading = ref(false)
  const cityError = ref<string | null>(null)

  /** City lists already fetched, keyed by county `dbName`. Not month-scoped. */
  const citiesCache = new Map<string, string[]>()
  /** City rows already fetched, keyed by `${month}|${county}|${city}`. */
  const cityRowsCache = new Map<string, MarketMonthlyByCity[]>()

  let citiesRequestId = 0
  let cityRowsRequestId = 0

  // --- National financing indicators. Month-scoped, but not county-scoped. ---

  /** `null` whenever the selected month has no indicator row. */
  const indicators = shallowRef<MarketIndicatorsMonthly | null>(null)
  const indicatorsCache = new Map<string, MarketIndicatorsMonthly | null>()
  let indicatorsRequestId = 0

  /** All rows for a county, keyed by the API's `county` string. */
  const rowsByCounty = computed(() => {
    const grouped = new Map<string, MarketMonthlyByCounty[]>()
    for (const row of rows.value) {
      const existing = grouped.get(row.county)
      if (existing) {
        existing.push(row)
      } else {
        grouped.set(row.county, [row])
      }
    }
    // Stable order so the panel doesn't reshuffle between counties.
    for (const list of grouped.values()) {
      list.sort((a, b) => a.main_type.localeCompare(b.main_type, 'hu'))
    }
    return grouped
  })

  /** Counties with data in the selected month. Drives the map's disabled state. */
  const countiesWithData = computed(
    () => new Set(COUNTIES.filter((c) => rowsByCounty.value.has(c.dbName)).map((c) => c.kshCode)),
  )

  const selectedCounty = computed<County | null>(
    () => COUNTIES.find((c) => c.kshCode === selectedCode.value) ?? null,
  )

  const selectedRows = computed<MarketMonthlyByCounty[]>(() => {
    const county = selectedCounty.value
    if (!county) return []
    return rowsByCounty.value.get(county.dbName) ?? []
  })

  const isEmpty = computed(() => !loading.value && !error.value && rows.value.length === 0)

  /** Select a county on the map. Resets any city filter - it belonged to the previous county. */
  function select(kshCode: number) {
    const next = selectedCode.value === kshCode ? null : kshCode
    selectedCode.value = next

    selectedCity.value = null
    cityRows.value = []
    cities.value = []
    cityError.value = null

    const county = next === null ? null : COUNTIES.find((c) => c.kshCode === next)
    if (county) void loadCities(county.dbName)
  }

  async function loadRows(month: string) {
    const cached = cache.get(month)
    if (cached) {
      rows.value = cached
      return
    }

    const id = ++requestId
    loading.value = true
    error.value = null
    try {
      const fetched = await fetchMarketMonthlyByCounty(month)
      if (id !== requestId) return // A newer month was picked while this was in flight.
      cache.set(month, fetched)
      rows.value = fetched
    } catch (cause) {
      if (id !== requestId) return
      error.value = cause instanceof Error ? cause.message : 'Ismeretlen hiba történt.'
      rows.value = []
    } finally {
      if (id === requestId) loading.value = false
    }
  }

  async function loadCities(countyDbName: string) {
    const cached = citiesCache.get(countyDbName)
    if (cached) {
      cities.value = cached
      return
    }

    const id = ++citiesRequestId
    try {
      const fetched = await fetchCitiesForCounty(countyDbName)
      if (id !== citiesRequestId) return // A different county was picked while this was in flight.
      fetched.sort((a, b) => a.localeCompare(b, 'hu'))
      citiesCache.set(countyDbName, fetched)
      cities.value = fetched
    } catch {
      if (id !== citiesRequestId) return
      // Fail soft: the filter just has no options. The county panel above still works.
      cities.value = []
    }
  }

  async function loadCityRows(month: string, county: string, city: string) {
    const key = `${month}|${county}|${city}`
    const cached = cityRowsCache.get(key)
    if (cached) {
      cityRows.value = cached
      return
    }

    const id = ++cityRowsRequestId
    cityLoading.value = true
    cityError.value = null
    try {
      const fetched = await fetchMarketMonthlyByCity(month, county, city)
      if (id !== cityRowsRequestId) return
      cityRowsCache.set(key, fetched)
      cityRows.value = fetched
    } catch (cause) {
      if (id !== cityRowsRequestId) return
      cityError.value = cause instanceof Error ? cause.message : 'Ismeretlen hiba történt.'
      cityRows.value = []
    } finally {
      if (id === cityRowsRequestId) cityLoading.value = false
    }
  }

  async function loadIndicators(month: string) {
    if (indicatorsCache.has(month)) {
      indicators.value = indicatorsCache.get(month) ?? null
      return
    }

    const id = ++indicatorsRequestId
    try {
      const fetched = await fetchMarketIndicatorsMonthly(month)
      if (id !== indicatorsRequestId) return
      indicatorsCache.set(month, fetched)
      indicators.value = fetched
    } catch {
      if (id !== indicatorsRequestId) return
      // Fail soft: the strip just hides. A broken feed must not take down the map.
      indicators.value = null
    }
  }

  /** Filter the selected county down to one city, or clear back to county-only with `null`. */
  async function selectCity(city: string | null) {
    selectedCity.value = city
    if (!city || !selectedCounty.value) {
      cityRows.value = []
      return
    }
    await loadCityRows(monthStart.value, selectedCounty.value.dbName, city)
  }

  /** Switch months. The selected county - and city, if any - is deliberately kept. */
  async function selectMonth(month: string) {
    if (!month || month === monthStart.value) return
    monthStart.value = month
    await Promise.all([loadRows(month), loadIndicators(month)])
    if (selectedCity.value && selectedCounty.value) {
      await loadCityRows(month, selectedCounty.value.dbName, selectedCity.value)
    }
  }

  async function load() {
    loading.value = true
    error.value = null
    try {
      months.value = await fetchMarketMonths()
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Ismeretlen hiba történt.'
      loading.value = false
      return
    }

    const latest = months.value[0]
    if (!latest) {
      // No months at all - let the empty state speak for itself.
      loading.value = false
      return
    }

    monthStart.value = latest
    await Promise.all([loadRows(latest), loadIndicators(latest)])
  }

  return {
    months,
    monthStart,
    rows,
    loading,
    error,
    isEmpty,
    rowsByCounty,
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
    cityLoading,
    cityError,
    selectCity,
    indicators,
  }
}
