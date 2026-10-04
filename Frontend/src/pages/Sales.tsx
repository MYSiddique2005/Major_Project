import { CheckCircle2, Clock, DollarSign, ShoppingCart } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { SearchBar } from '../components/common/SearchBar'
import { StatCard } from '../components/common/StatCard'
import { StatusBadge } from '../components/common/StatusBadge'
import { Toolbar } from '../components/common/Toolbar'
import { useApi } from '../hooks/useApi'
import { useDebounce } from '../hooks/useDebounce'
import { salesService } from '../services/salesService'
import { SALES_STATUSES, type Sale } from '../types'
import { formatCurrency, formatDate, formatNumber, formatPrice } from '../utils/format'

const COLUMNS: Column<Sale>[] = [
  { header: 'Order ID', render: (sale) => <span className="font-medium text-slate-900">{sale.id}</span> },
  { header: 'Customer', render: (sale) => sale.customer },
  { header: 'Product', render: (sale) => sale.product_name },
  { header: 'Quantity', render: (sale) => formatNumber(sale.quantity), align: 'right' },
  { header: 'Unit price', render: (sale) => formatPrice(sale.unit_price), align: 'right' },
  { header: 'Total', render: (sale) => formatCurrency(sale.total_amount), align: 'right' },
  { header: 'Order date', render: (sale) => formatDate(sale.order_date), className: 'whitespace-nowrap' },
  { header: 'Status', render: (sale) => <StatusBadge status={sale.status} /> },
]

export default function Sales() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const debouncedSearch = useDebounce(search)
  const stats = useApi(salesService.getStats, [])
  const sales = useApi(() => salesService.getSales({ search: debouncedSearch, status }), [debouncedSearch, status])

  return (
    <>
      <PageHeader title="Sales" subtitle="Customer sales orders across all products." />

      <QueryBoundary state={stats} resource="sales statistics">
        {(data) => (
          <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Revenue" value={formatCurrency(data.total_revenue)} icon={DollarSign} hint="Excludes cancelled orders" />
            <StatCard label="Orders" value={formatNumber(data.total_orders)} icon={ShoppingCart} />
            <StatCard label="Average order value" value={formatCurrency(data.average_order_value)} icon={CheckCircle2} />
            <StatCard label="Open orders" value={formatNumber(data.pending + data.processing)} icon={Clock} hint="Pending or processing" />
          </div>
        )}
      </QueryBoundary>

      <Card padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search orders, customers, products" />
          <FilterDropdown label="Statuses" value={status} options={SALES_STATUSES} onChange={setStatus} />
        </Toolbar>
        <QueryBoundary state={sales} resource="sales">
          {(rows) => (
            <DataTable
              caption="Sales orders"
              columns={COLUMNS}
              rows={rows}
              rowKey={(sale) => sale.id}
              onRowClick={(sale) => navigate(`/sales/${sale.id}`)}
              emptyMessage="No sales orders found."
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
