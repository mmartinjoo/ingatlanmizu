<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import type { ChartData, ChartOptions } from 'chart.js'
import type { MarketMonthlyChangeByCounty } from '@/api/types'
import { formatHuf, formatRatioDouble } from '@/utils/formatMarket'
import { formatMonthShort } from '@/utils/formatMonth'
import '@/utils/chart'

const props = defineProps<{
  title: string
  rows: MarketMonthlyChangeByCounty[]
}>()

/** Rise, fall, and "no previous month to compare against". */
const RISE = '#c92a2a'
const FALL = '#2f9e44'
const FLAT = '#adb5bd'

function colorOf(changePct: number | null): string {
  if (changePct === null || (changePct <= 0.9 && changePct >= -0.9)) return FLAT
  if (changePct > 0) return RISE
  if (changePct < 0) return FALL
  return FLAT
}

/** `formatRatioDouble` gives `1,24%`; a trend reads better with the sign spelled
 *  out. Null means the series starts here - there is nothing to label. */
function changeLabel(changePct: number | null): string {
  if (changePct === null) return ''
  const formatted = formatRatioDouble(changePct)
  return changePct > 0 ? `+${formatted}` : formatted
}

const chartData = computed<ChartData<'bar'>>(() => ({
  labels: props.rows.map((row) => formatMonthShort(row.month_start)),
  datasets: [
    {
      label: props.title,
      data: props.rows.map((row) => row.current_median_price_per_sqm),
      backgroundColor: props.rows.map((row) => colorOf(row.change_pct)),
    },
  ],
}))

const chartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  // The wrapper div owns the height. Without this Chart.js fights it on every
  // reactive update.
  maintainAspectRatio: false,
  layout: {
    // Datalabels sit above the bars and would otherwise clip at the top.
    padding: { top: 20 },
  },
  scales: {
    // County medians move a few percent a year. A non-zero baseline would turn
    // that noise into cliffs - the datalabels carry the real delta.
    y: {
      beginAtZero: true,
      // Full HUF labels are wide; a default ~11 ticks turns the axis into noise.
      ticks: { maxTicksLimit: 6, callback: (value) => formatHuf(Number(value)) },
    },
    x: { grid: { display: false } },
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => {
          const row = props.rows[context.dataIndex]
          const price = formatHuf(context.parsed.y)
          if (!row || row.change_pct === null) return `${price}/m²`
          return `${price}/m² (${changeLabel(row.change_pct)})`
        },
      },
    },
    datalabels: {
      anchor: 'end',
      align: 'end',
      offset: 2,
      font: { size: 10, weight: 600 },
      color: (context) => colorOf(props.rows[context.dataIndex]?.change_pct ?? null),
      formatter: (_value, context) => changeLabel(props.rows[context.dataIndex]?.change_pct ?? null),
    },
  },
}))
</script>

<template>
  <article class="trend-chart">
    <h3>{{ title }}</h3>
    <p v-if="rows.length === 0" class="hint">Ehhez a típushoz nincs trendadat.</p>
    <div v-else class="canvas-wrap">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </article>
</template>

<style scoped>
.trend-chart h3 {
  margin: 0 0 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  color: #6b6b6b;
}

.canvas-wrap {
  height: 16rem;
}

.hint {
  color: #6b6b6b;
  margin: 0;
}
</style>
