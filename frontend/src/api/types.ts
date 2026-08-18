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
