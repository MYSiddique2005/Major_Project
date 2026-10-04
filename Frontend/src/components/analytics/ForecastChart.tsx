import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { DemandForecast } from '../../types'
import { chartTheme } from '../../utils/chartTheme'
import { formatDate, formatNumber, formatShortDate } from '../../utils/format'
import { ChartTooltip } from '../dashboard/ChartTooltip'
import { ChartLegend } from './ChartLegend'

interface Point {
  week_start: string
  actual?: number
  forecast?: number
}

export function ForecastChart({ forecast }: { forecast: DemandForecast }) {
  const points: Point[] = forecast.history.map((week) => ({ week_start: week.week_start, actual: week.units }))
  // Start the forecast line at the last actual value so the two lines join.
  if (points.length > 0) points[points.length - 1].forecast = points[points.length - 1].actual
  forecast.forecast.forEach((week) => points.push({ week_start: week.week_start, forecast: week.units }))

  return (
    <div>
      <ChartLegend
        items={[
          { label: 'Actual units per week', color: chartTheme.series },
          { label: 'Forecast', color: chartTheme.series, dashed: true },
        ]}
      />
      <div className="h-64" role="img" aria-label={`Weekly demand history and forecast for ${forecast.product_name}`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid stroke={chartTheme.grid} vertical={false} />
            <XAxis
              dataKey="week_start"
              tickFormatter={formatShortDate}
              tick={{ fill: chartTheme.axis, fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: chartTheme.grid }}
              minTickGap={32}
            />
            <YAxis tick={{ fill: chartTheme.axis, fontSize: 12 }} tickLine={false} axisLine={false} width={44} />
            <Tooltip
              cursor={{ stroke: chartTheme.axis, strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                const point = payload?.[0]?.payload as Point | undefined
                if (!active || !point) return null
                const isForecast = point.actual === undefined
                return (
                  <ChartTooltip
                    title={`Week of ${formatDate(point.week_start)}`}
                    rows={[
                      {
                        label: isForecast ? 'Forecast units' : 'Actual units',
                        value: formatNumber((isForecast ? point.forecast : point.actual) ?? 0),
                      },
                    ]}
                  />
                )
              }}
            />
            <Line dataKey="actual" stroke={chartTheme.series} strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line
              dataKey="forecast"
              stroke={chartTheme.series}
              strokeWidth={2}
              strokeDasharray="5 4"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
