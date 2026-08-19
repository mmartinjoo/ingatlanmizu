import { get } from './client'
import type {
  MarketIndicatorsMonthly,
  MarketMonthlyByCity,
  MarketMonthlyByCounty,
  MarketMonthlyChangeByCounty,
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

/** Median price per sqm month by month for one county and property type, oldest
 *  first, ending at `monthStart`. `change_pct` is null on the first row when the
 *  pair has no earlier month. */
export function fetchMarketMonthlyChangeByCounty(
  monthStart: string,
  county: string,
  mainType: string,
) {
  return get<MarketMonthlyChangeByCounty[]>(
    `/api/market-monthly-change-by-county/${encodeURIComponent(county)}`,
    { month_start: monthStart, main_type: mainType },
  )
}
