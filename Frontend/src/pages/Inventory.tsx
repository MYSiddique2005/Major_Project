import { AlertOctagon, AlertTriangle, Boxes, PackageX } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { SearchBar } from '../components/common/SearchBar'
import { StatCard } from '../components/common/StatCard'
import { StatusBadge } from '../components/common/StatusBadge'
import { StockLevelBar } from '../components/common/StockLevelBar'
import { Toolbar } from '../components/common/Toolbar'
import { useApi } from '../hooks/useApi'
import { useDebounce } from '../hooks/useDebounce'
import { inventoryService } from '../services/inventoryService'
import { STOCK_STATUSES, type InventoryItem } from '../types'
import { formatNumber } from '../utils/format'

const COLUMNS: Column<InventoryItem>[] = [
  { header: 'Product', render: (item) => <span className="font-medium text-slate-900">{item.product_name}</span> },
  { header: 'SKU', render: (item) => item.sku, className: 'whitespace-nowrap' },
  { header: 'Warehouse', render: (item) => item.warehouse },
  { header: 'Current stock', render: (item) => formatNumber(item.current_stock), align: 'right' },
  { header: 'Safety stock', render: (item) => formatNumber(item.safety_stock), align: 'right' },
  { header: 'Reorder level', render: (item) => formatNumber(item.reorder_level), align: 'right' },
  {
    header: 'Level',
    render: (item) => <StockLevelBar current={item.current_stock} reorderLevel={item.reorder_level} status={item.status} />,
  },
  { header: 'Status', render: (item) => <StatusBadge status={item.status} /> },
]

export default function Inventory() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [warehouse, setWarehouse] = useState('')
  const debouncedSearch = useDebounce(search)
  const stats = useApi(inventoryService.getStats, [])
  const allItems = useApi(() => inventoryService.getInventory(), [])
  const items = useApi(
    () => inventoryService.getInventory({ search: debouncedSearch, status, warehouse }),
    [debouncedSearch, status, warehouse],
  )
  const warehouses = useMemo(
    () => [...new Set((allItems.data ?? []).map((item) => item.warehouse))].sort(),
    [allItems.data],
  )

  return (
    <>
      <PageHeader title="Inventory" subtitle="Stock on hand by product and warehouse." />

      <QueryBoundary state={stats} resource="inventory statistics">
        {(data) => (
          <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Inventory records" value={formatNumber(data.total_items)} icon={Boxes} hint={`${formatNumber(data.total_units)} units on hand`} />
            <StatCard label="Low stock" value={formatNumber(data.low_stock)} icon={AlertTriangle} tone="warning" hint="At or below reorder level" />
            <StatCard label="Critical" value={formatNumber(data.critical)} icon={AlertOctagon} tone="danger" hint="At or below half of safety stock" />
            <StatCard label="Out of stock" value={formatNumber(data.out_of_stock)} icon={PackageX} tone="danger" />
          </div>
        )}
      </QueryBoundary>

      <Card padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search products, SKUs, warehouses" />
          <FilterDropdown label="Statuses" value={status} options={STOCK_STATUSES} onChange={setStatus} />
          <FilterDropdown label="Warehouses" value={warehouse} options={warehouses} onChange={setWarehouse} />
        </Toolbar>
        <QueryBoundary state={items} resource="inventory">
          {(rows) => (
            <DataTable
              caption="Inventory records"
              columns={COLUMNS}
              rows={rows}
              rowKey={(item) => item.id}
              onRowClick={(item) => navigate(`/inventory/${item.id}`)}
              emptyMessage="No inventory records found."
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
