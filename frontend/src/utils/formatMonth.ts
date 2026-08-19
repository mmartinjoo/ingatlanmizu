const monthFormatter = new Intl.DateTimeFormat('hu-HU', { year: 'numeric', month: 'long' })

/** `2026-08-01` -> `2026. augusztus`. Returns an empty string for an empty input. */
export function formatMonth(monthStart: string): string {
  if (!monthStart) return ''
  return monthFormatter.format(new Date(`${monthStart}T00:00:00`))
}

const shortMonthFormatter = new Intl.DateTimeFormat('hu-HU', { month: 'long' })

/** `2026-08-01` -> `augusztus`. The long form is far too wide for a chart axis
 *  carrying a year of months. Returns an empty string for an empty input. */
export function formatMonthShort(monthStart: string): string {
  if (!monthStart) return ''
  return shortMonthFormatter.format(new Date(`${monthStart}T00:00:00`))
}
