import { useParams } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatusBadge } from '../components/common/StatusBadge'
import { TextLink } from '../components/common/TextLink'
import { useAuth } from '../context/AuthContext'
import { useApi } from '../hooks/useApi'
import { inventoryService } from '../services/inventoryService'
import { productService } from '../services/productService'
import type { InventoryItem } from '../types'
import { formatNumber, formatPrice } from '../utils/format'

const STOCK_COLUMNS: Column<InventoryItem>[] = [
  { header: 'Warehouse', render: (item) => <TextLink to={`/inventory/${item.id}`}>{item.warehouse}</TextLink> },
  { header: 'Current stock', render: (item) => formatNumber(item.current_stock), align: 'right' },
  { header: 'Safety stock', render: (item) => formatNumber(item.safety_stock), align: 'right' },
  { header: 'Reorder level', render: (item) => formatNumber(item.reorder_level), align: 'right' },
  { header: 'Status', render: (item) => <StatusBadge status={item.status} /> },
]

function StockByWarehouse({ productId }: { productId: string }) {
  const stock = useApi(() => inventoryService.getInventory({ product_id: productId }), [productId])
  return (
    <Card title="Stock by warehouse" padded={false} className="mt-6">
      <QueryBoundary state={stock} resource="stock levels">
        {(rows) => (
          <DataTable
            caption="Stock by warehouse"
            columns={STOCK_COLUMNS}
            rows={rows}
            rowKey={(item) => item.id}
            emptyMessage="No inventory records for this product."
          />
        )}
      </QueryBoundary>
    </Card>
  )
}

export default function ProductDetail() {
  const { id = '' } = useParams()
  const { hasPermission } = useAuth()
  const product = useApi(() => productService.getProduct(id), [id])

  return (
    <>
      <PageHeader
        title={product.data?.name ?? `Product ${id}`}
        back={{ to: '/products', label: 'Products' }}
        actions={
          hasPermission('analytics:view') &&
          product.data?.status === 'Active' && <TextLink to={`/analytics/products/${id}`}>View risk analysis</TextLink>
        }
      />
      <Card title="Product details">
        <QueryBoundary state={product} resource="product">
          {(data) => (
            <DetailList
              items={[
                { label: 'Product ID', value: data.id },
                { label: 'SKU', value: data.sku },
                { label: 'Status', value: <StatusBadge status={data.status} /> },
                { label: 'Category', value: data.category },
                {
                  label: 'Primary supplier',
                  value: hasPermission('suppliers:view') ? (
                    <TextLink to={`/suppliers/${data.supplier_id}`}>{data.supplier_name}</TextLink>
                  ) : (
                    data.supplier_name
                  ),
                },
                { label: 'Stock status', value: <StatusBadge status={data.stock_status} /> },
                { label: 'Selling price', value: formatPrice(data.price) },
                { label: 'Unit cost', value: formatPrice(data.unit_cost) },
                {
                  label: 'Total inventory',
                  value: `${formatNumber(data.current_stock)} (reorder level ${formatNumber(data.reorder_level)})`,
                },
              ]}
            />
          )}
        </QueryBoundary>
      </Card>
      {hasPermission('inventory:view') && <StockByWarehouse productId={id} />}
    </>
  )
}
