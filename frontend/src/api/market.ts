import { get } from './client'
import type { MarketMonthlyByCounty } from './types'

export function fetchMarketMonthlyByCounty(monthStart: string) {
  return get<MarketMonthlyByCounty[]>('/market-monthly-by-county', { month_start: monthStart })
}
