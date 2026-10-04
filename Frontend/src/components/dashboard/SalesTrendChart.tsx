import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { SalesTrendPoint } from '../../types'
import { chartTheme } from '../../utils/chartTheme'
import { formatCompactCurrency, formatCurrency, formatNumber } from '../../utils/format'
import { ChartTooltip } from './ChartTooltip'

export function SalesTrendChart({ data }: { data: SalesTrendPoint[] }) {
  return (
    <div className="h-64" role="img" aria-label="Monthly sales revenue for the last 12 months">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
          <CartesianGrid stroke={chartTheme.grid} vertical={false} />
          <XAxis
            dataKey="label"
            tickFormatter={(label: string) => label.split(' ')[0]}
            tick={{ fill: chartTheme.axis, fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: chartTheme.grid }}
          />
          <YAxis
            tickFormatter={(value: number) => formatCompactCurrency(value)}
            tick={{ fill: chartTheme.axis, fontSize: 12 }}
            tickLine={false}
            axisLine={false}
            width={56}
          />
          <Tooltip
            cursor={{ stroke: chartTheme.axis, strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              const point = payload?.[0]?.payload as SalesTrendPoint | undefined
              if (!active || !point) return null
              return (
                <ChartTooltip
                  title={point.label}
                  rows={[
                    { label: 'Revenue', value: formatCurrency(point.revenue) },
                    { label: 'Orders', value: formatNumber(point.orders) },
                  ]}
                />
              )
            }}
          />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke={chartTheme.series}
            strokeWidth={2}
            fill={chartTheme.series}
            fillOpacity={0.1}
            activeDot={{ r: 4, stroke: '#fff', strokeWidth: 2 }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
