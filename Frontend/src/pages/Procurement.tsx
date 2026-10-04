import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { SearchBar } from '../components/common/SearchBar'
import { StatusBadge } from '../components/common/StatusBadge'
import { Toolbar } from '../components/common/Toolbar'
import { PurchaseOrderForm } from '../components/procurement/PurchaseOrderForm'
import { useAuth } from '../context/AuthContext'
import { useApi } from '../hooks/useApi'
import { useDebounce } from '../hooks/useDebounce'
import { procurementService } from '../services/procurementService'
import { PURCHASE_ORDER_STATUSES, type PurchaseOrder } from '../types'
import { formatCurrency, formatDate, formatNumber, formatPrice } from '../utils/format'

const COLUMNS: Column<PurchaseOrder>[] = [
  { header: 'PO ID', render: (po) => <span className="font-medium text-slate-900">{po.id}</span> },
  { header: 'Supplier', render: (po) => po.supplier_name },
  { header: 'Product', render: (po) => po.product_name },
  { header: 'Quantity', render: (po) => formatNumber(po.quantity), align: 'right' },
  { header: 'Unit price', render: (po) => formatPrice(po.unit_price), align: 'right' },
  { header: 'Total', render: (po) => formatCurrency(po.total_amount), align: 'right' },
  { header: 'Order date', render: (po) => formatDate(po.order_date), className: 'whitespace-nowrap' },
  { header: 'Expected delivery', render: (po) => formatDate(po.expected_delivery), className: 'whitespace-nowrap' },
  { header: 'Status', render: (po) => <StatusBadge status={po.status} /> },
]

export default function Procurement() {
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [creating, setCreating] = useState(false)
  const debouncedSearch = useDebounce(search)
  const orders = useApi(
    () => procurementService.getPurchaseOrders({ search: debouncedSearch, status }),
    [debouncedSearch, status],
  )

  return (
    <>
      <PageHeader
        title="Procurement"
        subtitle="Purchase orders and their approval status."
        actions={
          hasPermission('procurement:create') && (
            <Button variant="primary" onClick={() => setCreating(true)}>
              <Plus className="size-4" aria-hidden />
              New purchase order
            </Button>
          )
        }
      />
      <Card padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search POs, suppliers, products" />
          <FilterDropdown label="Statuses" value={status} options={PURCHASE_ORDER_STATUSES} onChange={setStatus} />
        </Toolbar>
        <QueryBoundary state={orders} resource="purchase orders">
          {(rows) => (
            <DataTable
              caption="Purchase orders"
              columns={COLUMNS}
              rows={rows}
              rowKey={(po) => po.id}
              onRowClick={(po) => navigate(`/procurement/${po.id}`)}
              emptyMessage="No purchase orders found."
            />
          )}
        </QueryBoundary>
      </Card>

      {creating && (
        <PurchaseOrderForm
          onClose={() => setCreating(false)}
          onSaved={(po) => {
            setCreating(false)
            navigate(`/procurement/${po.id}`)
          }}
        />
      )}
    </>
  )
}
