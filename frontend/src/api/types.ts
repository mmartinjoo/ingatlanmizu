/** Mirrors the `MarketMonthlyByCounty` dataclass in the API. */
export interface MarketMonthlyByCounty {
  month_start: string
  county: string
  /** 'Ház' or 'Lakás'. */
  main_type: string
  listing_count: number
  new_build_count: number
  old_build_count: number
  unknown_build_count: number
  median_price_per_sqm: number
  median_year_of_building: number
  median_condition_score: number
  new_build_ratio: number | null
}
