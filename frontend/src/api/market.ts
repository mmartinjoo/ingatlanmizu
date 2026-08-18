import { get } from './client'
import type { MarketMonthlyByCounty } from './types'

/** Months that have county data, newest first, as `YYYY-MM-DD`. */
export function fetchMarketMonths() {
  return get<string[]>('/market-months')
}

export function fetchMarketMonthlyByCounty(monthStart: string) {
  return get<MarketMonthlyByCounty[]>('/market-monthly-by-county', { month_start: monthStart })
}
