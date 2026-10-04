import { useMemo, useState } from 'react'
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
import { productService } from '../services/productService'
import { PRODUCT_STATUSES, type Product } from '../types'
import { formatNumber, formatPrice } from '../utils/format'

const COLUMNS: Column<Product>[] = [
  { header: 'Product ID', render: (product) => product.id },
  { header: 'SKU', render: (product) => product.sku, className: 'whitespace-nowrap' },
  { header: 'Name', render: (product) => <span className="font-medium text-slate-900">{product.name}</span> },
  { header: 'Category', render: (product) => product.category },
  { header: 'Supplier', render: (product) => product.supplier_name },
  { header: 'Price', render: (product) => formatPrice(product.price), align: 'right' },
  { header: 'Inventory', render: (product) => formatNumber(product.current_stock), align: 'right' },
  { header: 'Reorder level', render: (product) => formatNumber(product.reorder_level), align: 'right' },
  { header: 'Stock', render: (product) => <StatusBadge status={product.stock_status} /> },
  { header: 'Status', render: (product) => <StatusBadge status={product.status} /> },
]

export default function Products() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [status, setStatus] = useState('')
  const debouncedSearch = useDebounce(search)
  const allProducts = useApi(() => productService.getProducts(), [])
  const products = useApi(
    () => productService.getProducts({ search: debouncedSearch, category, status }),
    [debouncedSearch, category, status],
  )
  const categories = useMemo(
    () => [...new Set((allProducts.data ?? []).map((product) => product.category))].sort(),
    [allProducts.data],
  )

  return (
    <>
      <PageHeader title="Products" subtitle="Product catalogue with supplier and stock position." />
      <Card padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search products, SKUs, categories" />
          <FilterDropdown label="Categories" value={category} options={categories} onChange={setCategory} />
          <FilterDropdown label="Statuses" value={status} options={PRODUCT_STATUSES} onChange={setStatus} />
        </Toolbar>
        <QueryBoundary state={products} resource="products">
          {(rows) => (
            <DataTable
              caption="Products"
              columns={COLUMNS}
              rows={rows}
              rowKey={(product) => product.id}
              onRowClick={(product) => navigate(`/products/${product.id}`)}
              emptyMessage="No products found."
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
