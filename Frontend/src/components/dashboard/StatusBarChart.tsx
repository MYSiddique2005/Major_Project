import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { StatusCount } from '../../types'
import { chartTheme } from '../../utils/chartTheme'
import { ChartTooltip } from './ChartTooltip'

interface StatusBarChartProps {
  data: StatusCount[]
  /** Noun for the counted records, e.g. "records" or "orders". */
  unit: string
  ariaLabel: string
  /** Per-status colours; statuses without one use the default series colour. */
  colors?: Record<string, string>
}

const ROW_HEIGHT = 34

/** Horizontal bars, one per status, labelled directly with their counts. */
export function StatusBarChart({ data, unit, ariaLabel, colors = {} }: StatusBarChartProps) {
  return (
    <div style={{ height: data.length * ROW_HEIGHT + 16 }} role="img" aria-label={ariaLabel}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 32, bottom: 0, left: 0 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="status"
            width={130}
            tick={{ fill: chartTheme.axis, fontSize: 12, width: 130 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            cursor={{ fill: '#f1f5f9' }}
            content={({ active, payload }) => {
              const point = payload?.[0]?.payload as StatusCount | undefined
              if (!active || !point) return null
              return <ChartTooltip title={point.status} rows={[{ label: unit, value: String(point.count) }]} />
            }}
          />
          <Bar dataKey="count" barSize={16} radius={[0, 4, 4, 0]} isAnimationActive={false}>
            {data.map((entry) => (
              <Cell key={entry.status} fill={colors[entry.status] ?? chartTheme.series} />
            ))}
            <LabelList dataKey="count" position="right" fill={chartTheme.ink} fontSize={12} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
