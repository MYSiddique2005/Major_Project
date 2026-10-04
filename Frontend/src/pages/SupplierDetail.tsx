import { useParams } from 'react-router-dom'

import { Card } from '../components/common/Card'
import { DetailList } from '../components/common/DetailList'
import { EmptyState } from '../components/common/EmptyState'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatusBadge } from '../components/common/StatusBadge'
import { TextLink } from '../components/common/TextLink'
import { useApi } from '../hooks/useApi'
import { supplierService } from '../services/supplierService'

export default function SupplierDetail() {
  const { id = '' } = useParams()
  const supplier = useApi(() => supplierService.getSupplier(id), [id])

  return (
    <>
      <PageHeader title={supplier.data?.name ?? `Supplier ${id}`} back={{ to: '/suppliers', label: 'Suppliers' }} />
      <QueryBoundary state={supplier} resource="supplier">
        {(data) => (
          <div className="space-y-6">
            <Card title="Supplier details">
              <DetailList
                items={[
                  { label: 'Supplier ID', value: data.id },
                  { label: 'Status', value: <StatusBadge status={data.status} /> },
                  { label: 'Country', value: data.country },
                  { label: 'Contact', value: data.contact_name },
                  { label: 'Email', value: <a href={`mailto:${data.email}`} className="text-brand-700 hover:underline">{data.email}</a> },
                  { label: 'Phone', value: data.phone },
                  { label: 'Average delivery time', value: `${data.avg_delivery_days.toFixed(1)} days` },
                  { label: 'On-time delivery', value: `${data.delivery_reliability.toFixed(0)}%` },
                ]}
              />
            </Card>
            <Card title="Products supplied">
              {data.products_supplied.length === 0 ? (
                <EmptyState message="This supplier has no products." />
              ) : (
                <ul className="divide-y divide-slate-100">
                  {data.products_supplied.map((product) => (
                    <li key={product.id} className="flex items-center justify-between py-2 text-sm first:pt-0 last:pb-0">
                      <TextLink to={`/products/${product.id}`}>{product.name}</TextLink>
                      <span className="text-slate-500">{product.sku}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        )}
      </QueryBoundary>
    </>
  )
}
