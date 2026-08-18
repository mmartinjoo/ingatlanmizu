const huf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })
const percent = new Intl.NumberFormat('hu-HU', { maximumFractionDigits: 1 })

export function formatHuf(value: number | null): string {
  return value === null ? '–' : `${huf.format(value)} Ft`
}

export function formatRatio(value: number | null, nullValue: string = '-'): string {
  return value === null ? nullValue : `${percent.format(value)}%`
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
