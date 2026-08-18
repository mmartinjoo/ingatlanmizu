import { computed, ref, shallowRef } from 'vue'
import { fetchMarketMonths, fetchMarketMonthlyByCounty } from '@/api/market'
import type { MarketMonthlyByCounty } from '@/api/types'
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

  function select(kshCode: number) {
    selectedCode.value = selectedCode.value === kshCode ? null : kshCode
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

  /** Switch months. The selected county is deliberately kept. */
  async function selectMonth(month: string) {
    if (!month || month === monthStart.value) return
    monthStart.value = month
    await loadRows(month)
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
    await loadRows(latest)
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
  }
}
