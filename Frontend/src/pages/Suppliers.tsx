import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { SearchBar } from '../components/common/SearchBar'
import { StatusBadge } from '../components/common/StatusBadge'
import { Toolbar } from '../components/common/Toolbar'
import { useApi } from '../hooks/useApi'
import { useDebounce } from '../hooks/useDebounce'
import { supplierService } from '../services/supplierService'
import { SUPPLIER_STATUSES, type Supplier } from '../types'

const COLUMNS: Column<Supplier>[] = [
  { header: 'Supplier ID', render: (supplier) => supplier.id },
  { header: 'Name', render: (supplier) => <span className="font-medium text-slate-900">{supplier.name}</span> },
  {
    header: 'Contact',
    render: (supplier) => (
      <>
        <span className="block">{supplier.contact_name}</span>
        <span className="block text-xs text-slate-500">{supplier.email}</span>
      </>
    ),
  },
  { header: 'Products supplied', render: (supplier) => supplier.products_supplied.length, align: 'right' },
  { header: 'Avg. delivery', render: (supplier) => `${supplier.avg_delivery_days.toFixed(1)} days`, align: 'right' },
  { header: 'On-time delivery', render: (supplier) => `${supplier.delivery_reliability.toFixed(0)}%`, align: 'right' },
  { header: 'Status', render: (supplier) => <StatusBadge status={supplier.status} /> },
]

export default function Suppliers() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const debouncedSearch = useDebounce(search)
  const suppliers = useApi(
    () => supplierService.getSuppliers({ search: debouncedSearch, status }),
    [debouncedSearch, status],
  )

  return (
    <>
      <PageHeader title="Suppliers" subtitle="Supplier directory and delivery performance." />
      <Card padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search suppliers, contacts, countries" />
          <FilterDropdown label="Statuses" value={status} options={SUPPLIER_STATUSES} onChange={setStatus} />
        </Toolbar>
        <QueryBoundary state={suppliers} resource="suppliers">
          {(rows) => (
            <DataTable
              caption="Suppliers"
              columns={COLUMNS}
              rows={rows}
              rowKey={(supplier) => supplier.id}
              onRowClick={(supplier) => navigate(`/suppliers/${supplier.id}`)}
              emptyMessage="No suppliers found."
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
