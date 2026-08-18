const huf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })
const percent = new Intl.NumberFormat('hu-HU', { maximumFractionDigits: 1 })
/** Interest rates are quoted to 2 decimals: 5,75% must not round to 5,8%. */
const rate = new Intl.NumberFormat('hu-HU', { maximumFractionDigits: 2 })

export function formatHuf(value: number | null): string {
  return value === null ? '–' : `${huf.format(value)} Ft`
}

export function formatRatio(value: number | null, nullValue: string = '-'): string {
  return value === null ? nullValue : `${percent.format(value)}%`
}

/** For interest rates (alapkamat, THM), where 1 decimal loses real precision. */
export function formatRate(value: number | null): string {
  return value === null ? '–' : `${rate.format(value)}%`
}

export function formatCount(value: number | null): string {
  return value === null ? '–' : huf.format(value)
}

export function formatConditionScore(value: number): string {
  switch (value) {
    case 1:
      return 'Felújítandó'
    case 2:
      return 'Átlagos'
    case 3:
      return 'Jó állapotú'
    case 4:
      return 'Újszerű'
    case 5:
      return 'Új építésű'
    default:
      return '–'
  }
}
