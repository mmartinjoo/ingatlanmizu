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

/** Mirrors the `MarketMonthlyByCity` dataclass in the API. */
export interface MarketMonthlyByCity {
  month_start: string
  county: string
  city: string
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

/** Mirrors the `MarketIndicatorsMonthly` dataclass in the API.
 *  National figures - not county-scoped. The endpoint returns `null` for a
 *  month with no indicator row. */
export interface MarketIndicatorsMonthly {
  month_start: string
  /** MNB base rate, percent. */
  base_rate: number
  /** KSH inflation, percent. */
  inflation: number
  /** THM (annual percentage rate) across the surveyed mortgage products. */
  median_apr: number
  lowest_apr: number
  highest_apr: number
  /** HUF per month. See LOAN_ASSUMPTION in utils/mortgage.ts for the terms. */
  median_monthly_installment: number
  lowest_monthly_installment: number
  highest_monthly_installment: number
}

/** Mirrors the `MarketMonthlyChangeByCounty` dataclass in the API.
 *  One row per month, oldest first, covering the 12 months up to and including
 *  the requested `month_start` - so up to 13 rows, the window being inclusive
 *  at both ends. */
export interface MarketMonthlyChangeByCounty {
  month_start: string
  county: string
  /** 'Ház' or 'Lakás'. */
  main_type: string
  current_median_price_per_sqm: number
  /** Month-over-month change, percent. `null` for the first month the
   *  county/type pair has data - the API's dataclass says `float`, but `lag()`
   *  yields no previous value there. */
  change_pct: number | null
}

export interface ListingCount {
  count: number
}