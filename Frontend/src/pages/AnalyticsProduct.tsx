import { FilePlus2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { ForecastChart } from '../components/analytics/ForecastChart'
import { RiskBadge } from '../components/analytics/RiskBadge'
import { WhatIfPanel } from '../components/analytics/WhatIfPanel'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { TextLink } from '../components/common/TextLink'
import { PurchaseOrderForm } from '../components/procurement/PurchaseOrderForm'
import { useAuth } from '../context/AuthContext'
import { useApi } from '../hooks/useApi'
import { analyticsService } from '../services/analyticsService'
import type { ForecastMethod } from '../types'
import { formatDate, formatNumber } from '../utils/format'

const METHOD_LABELS: Record<ForecastMethod, string> = {
  moving_average: '4-week moving average',
  linear_trend: '12-week linear trend',
}

const formatError = (wape: number | null) => (wape === null ? 'not enough history' : `${(wape * 100).toFixed(0)}%`)

export default function AnalyticsProduct() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const [method, setMethod] = useState<ForecastMethod | ''>('')
  const [drafting, setDrafting] = useState(false)
  const risk = useApi(() => analyticsService.getProductRisk(id), [id])
  const forecast = useApi(() => analyticsService.getForecast(id, method || undefined), [id, method])

  const item = risk.data
  const canDraft = item && item.suggested_order_quantity > 0 && item.suggested_supplier_id && hasPermission('procurement:create')

  return (
    <>
      <PageHeader
        title={item ? `${item.product_name}: risk analysis` : `Risk analysis ${id}`}
        subtitle="Calculated from ERP data with fixed rules and simple statistics. No AI model is involved."
        back={{ to: '/analytics', label: 'Analytics' }}
        actions={
          canDraft && (
            <Button variant="primary" onClick={() => setDrafting(true)}>
              <FilePlus2 className="size-4" aria-hidden />
              Draft purchase order ({formatNumber(item.suggested_order_quantity)} units)
            </Button>
          )
        }
      />

      <div className="space-y-6">
        <QueryBoundary state={risk} resource="risk analysis">
          {(data) => (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <Card title="Stock position" className="lg:col-span-2">
                <DetailList
                  items={[
                    { label: 'Stockout risk', value: <RiskBadge level={data.risk_level} /> },
                    { label: 'On hand (all warehouses)', value: formatNumber(data.on_hand) },
                    { label: 'Safety stock', value: formatNumber(data.safety_stock) },
                    {
                      label: 'Demand, last 28 days',
                      value: `${data.avg_daily_demand} units/day${
                        data.demand_trend_pct === null
                          ? ''
                          : ` (${data.demand_trend_pct > 0 ? '+' : ''}${data.demand_trend_pct.toFixed(0)}% on previous 28 days)`
                      }`,
                    },
                    { label: 'Days of cover', value: data.days_of_cover?.toFixed(1) ?? '—' },
                    { label: 'Projected stockout', value: formatDate(data.projected_stockout_date) },
                    {
                      label: 'Supplier',
                      value: hasPermission('suppliers:view') ? (
                        <TextLink to={`/suppliers/${data.supplier_id}`}>{data.supplier_name}</TextLink>
                      ) : (
                        data.supplier_name
                      ),
                    },
                    { label: 'Lead time', value: `${data.lead_time_days} days (${data.lead_time_source})` },
                    { label: 'Reorder point', value: formatNumber(data.reorder_point) },
                    {
                      label: 'On order',
                      value: data.inbound_units
                        ? `${formatNumber(data.inbound_units)} (next ${formatDate(data.next_inbound_date)})`
                        : '0',
                    },
                    { label: 'Overdue from supplier', value: formatNumber(data.overdue_inbound_units) },
                    { label: 'In orders not yet placed', value: formatNumber(data.awaiting_approval_units) },
                  ]}
                />
              </Card>

              <Card title="Evidence" subtitle="The facts behind the risk level">
                {data.drivers.length === 0 ? (
                  <p className="text-sm text-slate-600">No risk indicators for this product.</p>
                ) : (
                  <ul className="list-disc space-y-2 pl-5 text-sm text-slate-700">
                    {data.drivers.map((driver) => (
                      <li key={driver}>{driver}</li>
                    ))}
                  </ul>
                )}
                <p className="mt-4 border-t border-slate-200 pt-3 text-sm text-slate-700">
                  {data.suggested_order_quantity > 0 ? (
                    <>
                      <span className="font-medium">Suggested order:</span> {formatNumber(data.suggested_order_quantity)} units
                      {data.suggested_supplier_name ? ` from ${data.suggested_supplier_name}` : ' (no active supplier available)'}.
                      Covers lead time plus a 14-day review period and restores safety stock.
                    </>
                  ) : (
                    'No new order suggested: stock plus existing orders are above the reorder point.'
                  )}
                </p>
              </Card>
            </div>
          )}
        </QueryBoundary>

        <Card
          title="Demand forecast"
          subtitle="Weekly units sold over the last 26 weeks and the next 8 weeks"
          actions={
            <select
              className="field w-auto"
              value={method}
              onChange={(event) => setMethod(event.target.value as ForecastMethod | '')}
              aria-label="Forecast method"
            >
              <option value="">Best method (lowest error)</option>
              <option value="moving_average">{METHOD_LABELS.moving_average}</option>
              <option value="linear_trend">{METHOD_LABELS.linear_trend}</option>
            </select>
          }
        >
          <QueryBoundary state={forecast} resource="demand forecast">
            {(data) => (
              <>
                <ForecastChart forecast={data} />
                <p className="mt-3 text-xs text-slate-500">
                  Method: {METHOD_LABELS[data.method]} ({data.method_selection}). Forecast average{' '}
                  {formatNumber(Math.round(data.avg_weekly_forecast))} units/week. One-week-ahead error over the last 8 weeks:
                  moving average {formatError(data.backtest_wape.moving_average)}, linear trend{' '}
                  {formatError(data.backtest_wape.linear_trend)}.
                </p>
              </>
            )}
          </QueryBoundary>
        </Card>

        <Card title="What-if analysis" subtitle="Project stock under different demand, delivery delay or a new order. Nothing is saved.">
          <WhatIfPanel productId={id} />
        </Card>
      </div>

      {drafting && item && (
        <PurchaseOrderForm
          defaults={{
            supplier_id: item.suggested_supplier_id ?? undefined,
            product_id: item.product_id,
            quantity: item.suggested_order_quantity,
            reason: `Reorder suggested by stock-risk analytics (${item.risk_level.toLowerCase()} risk)`,
          }}
          onClose={() => setDrafting(false)}
          onSaved={(po) => navigate(`/procurement/${po.id}`)}
        />
      )}
    </>
  )
}
