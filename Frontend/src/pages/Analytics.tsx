import { AlertOctagon, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { RiskBadge } from '../components/analytics/RiskBadge'
import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { SearchBar } from '../components/common/SearchBar'
import { StatCard } from '../components/common/StatCard'
import { Toolbar } from '../components/common/Toolbar'
import { useApi } from '../hooks/useApi'
import { useDebounce } from '../hooks/useDebounce'
import { analyticsService } from '../services/analyticsService'
import { RISK_LEVELS, type StockRiskItem, type SupplierPerformanceItem } from '../types'
import { formatNumber } from '../utils/format'

const formatTrend = (trend: number | null) => (trend === null ? '—' : `${trend > 0 ? '+' : ''}${trend.toFixed(0)}%`)

const STOCK_COLUMNS: Column<StockRiskItem>[] = [
  { header: 'Product', render: (item) => <span className="font-medium text-slate-900">{item.product_name}</span>, className: 'min-w-48' },
  { header: 'Risk', render: (item) => <RiskBadge level={item.risk_level} /> },
  { header: 'On hand', render: (item) => formatNumber(item.on_hand), align: 'right' },
  { header: 'Safety stock', render: (item) => formatNumber(item.safety_stock), align: 'right' },
  { header: 'Demand / day', render: (item) => item.avg_daily_demand.toFixed(1), align: 'right' },
  { header: 'Trend (28 d)', render: (item) => formatTrend(item.demand_trend_pct), align: 'right' },
  { header: 'Days of cover', render: (item) => item.days_of_cover?.toFixed(0) ?? '—', align: 'right' },
  { header: 'Lead time', render: (item) => `${item.lead_time_days.toFixed(1)} d`, align: 'right' },
  { header: 'On order', render: (item) => formatNumber(item.inbound_units + item.overdue_inbound_units), align: 'right' },
  {
    header: 'Suggested order',
    render: (item) => (item.suggested_order_quantity ? formatNumber(item.suggested_order_quantity) : '—'),
    align: 'right',
  },
]

const SUPPLIER_COLUMNS: Column<SupplierPerformanceItem>[] = [
  { header: 'Supplier', render: (item) => <span className="font-medium text-slate-900">{item.supplier_name}</span>, className: 'min-w-44' },
  { header: 'Risk', render: (item) => <RiskBadge level={item.risk_level} /> },
  { header: 'Deliveries', render: (item) => item.deliveries_analyzed, align: 'right' },
  { header: 'On time', render: (item) => (item.on_time_rate === null ? '—' : `${item.on_time_rate.toFixed(0)}%`), align: 'right' },
  { header: 'Avg. delay', render: (item) => (item.avg_delay_days === null ? '—' : `${item.avg_delay_days.toFixed(1)} d`), align: 'right' },
  { header: 'Avg. lead time', render: (item) => (item.avg_lead_time_days === null ? '—' : `${item.avg_lead_time_days.toFixed(1)} d`), align: 'right' },
  { header: 'Delay trend', render: (item) => <span className="inline-block first-letter:uppercase">{item.delay_trend}</span> },
  { header: 'Overdue orders', render: (item) => item.overdue_orders, align: 'right' },
  { header: 'Evidence', render: (item) => <span className="text-slate-600">{item.drivers.join(' ')}</span>, className: 'min-w-72' },
]

export default function Analytics() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('')
  const debouncedSearch = useDebounce(search)
  const allRisk = useApi(() => analyticsService.getStockRisk(), [])
  const stockRisk = useApi(() => analyticsService.getStockRisk({ search: debouncedSearch, level }), [debouncedSearch, level])
  const suppliers = useApi(analyticsService.getSupplierPerformance, [])

  return (
    <>
      <PageHeader
        title="Analytics"
        subtitle="Stockout and supplier risk calculated from sales, inventory and purchase-order data using fixed rules. No AI model is involved."
      />

      <QueryBoundary state={allRisk} resource="risk summary">
        {(items) => {
          const count = (riskLevel: string) => items.filter((item) => item.risk_level === riskLevel).length
          return (
            <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard label="Critical stock risk" value={String(count('Critical'))} icon={AlertOctagon} tone="danger" hint="Out of stock and still selling" />
              <StatCard label="High stock risk" value={String(count('High'))} icon={ShieldAlert} tone="danger" hint="Likely to run out before resupply" />
              <StatCard label="Medium stock risk" value={String(count('Medium'))} icon={AlertTriangle} tone="warning" hint="Below safety stock or thin cover" />
              <StatCard label="Low stock risk" value={String(count('Low'))} icon={CheckCircle2} />
            </div>
          )
        }}
      </QueryBoundary>

      <Card title="Stockout risk by product" subtitle="Select a product for its evidence, demand forecast and what-if analysis." padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search products, SKUs, suppliers" />
          <FilterDropdown label="Risk levels" value={level} options={RISK_LEVELS} onChange={setLevel} />
        </Toolbar>
        <QueryBoundary state={stockRisk} resource="stock risk">
          {(rows) => (
            <DataTable
              caption="Stockout risk by product"
              columns={STOCK_COLUMNS}
              rows={rows}
              rowKey={(item) => item.product_id}
              onRowClick={(item) => navigate(`/analytics/products/${item.product_id}`)}
              emptyMessage="No products match."
            />
          )}
        </QueryBoundary>
      </Card>

      <Card
        title="Supplier delivery performance"
        subtitle="Measured from delivered and open purchase orders. Few deliveries per supplier, so treat percentages with care."
        padded={false}
        className="mt-6"
      >
        <QueryBoundary state={suppliers} resource="supplier performance">
          {(rows) => (
            <DataTable
              caption="Supplier delivery performance"
              columns={SUPPLIER_COLUMNS}
              rows={rows}
              rowKey={(item) => item.supplier_id}
              onRowClick={(item) => navigate(`/suppliers/${item.supplier_id}`)}
              emptyMessage="No suppliers found."
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
