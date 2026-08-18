import { computed, ref, shallowRef } from 'vue'
import { fetchMarketMonthlyByCounty } from '@/api/market'
import type { MarketMonthlyByCounty } from '@/api/types'
import { COUNTIES, type County } from '@/data/counties'

/** First day of the current month, as `YYYY-MM-DD`. */
export function currentMonthStart(today = new Date()): string {
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}-01`
}

export function useCountyMarket() {
  const monthStart = ref(currentMonthStart())
  const rows = shallowRef<MarketMonthlyByCounty[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedCode = ref<number | null>(null)

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

  /** Counties that actually have data this month. Drives the map's disabled state. */
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

  async function load() {
    loading.value = true
    error.value = null
    try {
      rows.value = await fetchMarketMonthlyByCounty(monthStart.value)
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Ismeretlen hiba történt.'
      rows.value = []
    } finally {
      loading.value = false
    }
  }

  return {
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
    load,
  }
}
