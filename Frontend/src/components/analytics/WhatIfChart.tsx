import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { WhatIfResult } from '../../types'
import { chartTheme } from '../../utils/chartTheme'
import { formatDate, formatNumber, formatShortDate } from '../../utils/format'
import { ChartTooltip } from '../dashboard/ChartTooltip'
import { ChartLegend } from './ChartLegend'

interface Point {
  date: string
  baseline: number
  scenario: number
}

export function WhatIfChart({ result }: { result: WhatIfResult }) {
  const points: Point[] = result.baseline.points.map((point, index) => ({
    date: point.date,
    baseline: point.stock,
    scenario: result.scenario.points[index].stock,
  }))

  return (
    <div>
      <ChartLegend
        items={[
          { label: 'Baseline', color: chartTheme.series },
          { label: 'Scenario', color: chartTheme.series2 },
          { label: `Safety stock (${formatNumber(result.safety_stock)})`, color: chartTheme.axis, dashed: true },
        ]}
      />
      <div className="h-64" role="img" aria-label={`Projected stock for ${result.product_name}: baseline versus scenario`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid stroke={chartTheme.grid} vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatShortDate}
              tick={{ fill: chartTheme.axis, fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: chartTheme.grid }}
              minTickGap={40}
            />
            <YAxis tick={{ fill: chartTheme.axis, fontSize: 12 }} tickLine={false} axisLine={false} width={52} />
            <ReferenceLine y={result.safety_stock} stroke={chartTheme.axis} strokeDasharray="5 4" />
            <Tooltip
              cursor={{ stroke: chartTheme.axis, strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                const point = payload?.[0]?.payload as Point | undefined
                if (!active || !point) return null
                return (
                  <ChartTooltip
                    title={formatDate(point.date)}
                    rows={[
                      { label: 'Baseline stock', value: formatNumber(Math.round(point.baseline)) },
                      { label: 'Scenario stock', value: formatNumber(Math.round(point.scenario)) },
                    ]}
                  />
                )
              }}
            />
            <Line type="linear" dataKey="baseline" stroke={chartTheme.series} strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="linear" dataKey="scenario" stroke={chartTheme.series2} strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
