import {
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  LinearScale,
  Tooltip,
} from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'

/** Chart.js ships nothing registered by default. Registering only the bar
 *  pieces here - once, in a module every chart imports - keeps the rest of the
 *  library tree-shaken out and avoids each component re-registering. */
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, ChartDataLabels)
