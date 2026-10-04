import { useParams } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatusBadge } from '../components/common/StatusBadge'
import { StockLevelBar } from '../components/common/StockLevelBar'
import { TextLink } from '../components/common/TextLink'
import { useApi } from '../hooks/useApi'
import { inventoryService } from '../services/inventoryService'
import { formatDate, formatNumber } from '../utils/format'

export default function InventoryDetail() {
  const { id = '' } = useParams()
  const item = useApi(() => inventoryService.getItem(id), [id])

  return (
    <>
      <PageHeader title={`Inventory record ${id}`} back={{ to: '/inventory', label: 'Inventory' }} />
      <Card title="Stock details">
        <QueryBoundary state={item} resource="inventory record">
          {(data) => (
            <DetailList
              items={[
                { label: 'Product', value: <TextLink to={`/products/${data.product_id}`}>{data.product_name}</TextLink> },
                { label: 'SKU', value: data.sku },
                { label: 'Warehouse', value: data.warehouse },
                { label: 'Status', value: <StatusBadge status={data.status} /> },
                { label: 'Current stock', value: formatNumber(data.current_stock) },
                {
                  label: 'Stock level',
                  value: <StockLevelBar current={data.current_stock} reorderLevel={data.reorder_level} status={data.status} />,
                },
                { label: 'Safety stock', value: formatNumber(data.safety_stock) },
                { label: 'Reorder level', value: formatNumber(data.reorder_level) },
                { label: 'Last updated', value: formatDate(data.last_updated) },
              ]}
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
