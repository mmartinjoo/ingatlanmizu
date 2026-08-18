/**
 * Assumptions behind the affordability estimate.
 *
 * Term and LTV deliberately match the Bankmonitor query the indicator data
 * comes from (40 M Ft loan on a 60 M Ft property over 20 years), so the
 * estimate is consistent with the median THM it is applied to rather than
 * mixing two different sets of terms.
 */
export const REFERENCE_SIZE_SQM = 75
export const LTV = 2 / 3
export const TERM_YEARS = 20

/** The terms behind the API's own `*_monthly_installment` figures. */
export const LOAN_ASSUMPTION = '40 M Ft hitel, 20 év, 60 M Ft használt lakásra'

/**
 * Standard annuity payment.
 *
 * `annualRatePercent` is a percentage (7.16), not a fraction. We feed it the
 * median THM, which includes fees, so the result is a slight over-estimate of
 * a pure-interest payment - fine for an "approximately" figure.
 */
export function monthlyPayment(
  principal: number,
  annualRatePercent: number,
  years: number,
): number {
  const months = years * 12
  if (months <= 0) return 0

  const monthlyRate = annualRatePercent / 100 / 12
  if (monthlyRate === 0) return principal / months

  const growth = Math.pow(1 + monthlyRate, months)
  return (principal * (monthlyRate * growth)) / (growth - 1)
}

/** Estimated purchase price of a reference-sized home at a given price per m². */
export function referencePrice(medianPricePerSqm: number): number {
  return medianPricePerSqm * REFERENCE_SIZE_SQM
}

/** Estimated monthly payment for a reference home financed at the given THM. */
export function referenceMonthlyPayment(medianPricePerSqm: number, annualRatePercent: number) {
  return monthlyPayment(referencePrice(medianPricePerSqm) * LTV, annualRatePercent, TERM_YEARS)
}
