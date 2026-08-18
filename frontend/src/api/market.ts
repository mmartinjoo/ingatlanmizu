import { get } from './client'
import type {
  MarketIndicatorsMonthly,
  MarketMonthlyByCity,
  MarketMonthlyByCounty,
} from './types'

/** Months that have county data, newest first, as `YYYY-MM-DD`. */
export function fetchMarketMonths() {
  return get<string[]>('/api/market-months')
}

export function fetchMarketMonthlyByCounty(monthStart: string) {
  return get<MarketMonthlyByCounty[]>('/api/market-monthly-by-county', { month_start: monthStart })
}

/** Distinct city names in a county. Not month-scoped. Order is arbitrary - caller sorts. */
export function fetchCitiesForCounty(county: string) {
  return get<string[]>(`/api/counties/${encodeURIComponent(county)}/cities`)
}

export function fetchMarketMonthlyByCity(monthStart: string, county: string, city: string) {
  return get<MarketMonthlyByCity[]>('/api/market-monthly-by-city', {
    month_start: monthStart,
    county,
    city,
  })
}

/** National financing indicators. `null` when the month has no data. */
export function fetchMarketIndicatorsMonthly(monthStart: string) {
  return get<MarketIndicatorsMonthly | null>('/api/market-indicators-monthly', {
    month_start: monthStart,
  })
}
