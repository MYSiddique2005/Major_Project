import { useParams } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatusBadge } from '../components/common/StatusBadge'
import { TextLink } from '../components/common/TextLink'
import { useApi } from '../hooks/useApi'
import { salesService } from '../services/salesService'
import { formatCurrency, formatDate, formatNumber, formatPrice } from '../utils/format'

export default function SaleDetail() {
  const { id = '' } = useParams()
  const sale = useApi(() => salesService.getSale(id), [id])

  return (
    <>
      <PageHeader title={`Sales order ${id}`} back={{ to: '/sales', label: 'Sales' }} />
      <Card title="Order details">
        <QueryBoundary state={sale} resource="sales order">
          {(data) => (
            <DetailList
              items={[
                { label: 'Order ID', value: data.id },
                { label: 'Status', value: <StatusBadge status={data.status} /> },
                { label: 'Order date', value: formatDate(data.order_date) },
                { label: 'Customer', value: data.customer },
                { label: 'Product', value: <TextLink to={`/products/${data.product_id}`}>{data.product_name}</TextLink> },
                { label: 'SKU', value: data.sku },
                { label: 'Quantity', value: formatNumber(data.quantity) },
                { label: 'Unit price', value: formatPrice(data.unit_price) },
                { label: 'Total amount', value: formatCurrency(data.total_amount) },
              ]}
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
