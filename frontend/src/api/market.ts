import { get } from './client'
import type { MarketMonthlyByCity, MarketMonthlyByCounty } from './types'

/** Months that have county data, newest first, as `YYYY-MM-DD`. */
export function fetchMarketMonths() {
  return get<string[]>('/market-months')
}

export function fetchMarketMonthlyByCounty(monthStart: string) {
  return get<MarketMonthlyByCounty[]>('/market-monthly-by-county', { month_start: monthStart })
}

/** Distinct city names in a county. Not month-scoped. Order is arbitrary - caller sorts. */
export function fetchCitiesForCounty(county: string) {
  return get<string[]>(`/counties/${encodeURIComponent(county)}/cities`)
}

export function fetchMarketMonthlyByCity(monthStart: string, county: string, city: string) {
  return get<MarketMonthlyByCity[]>('/market-monthly-by-city', {
    month_start: monthStart,
    county,
    city,
  })
}
