import { Pencil, Send, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatusBadge } from '../components/common/StatusBadge'
import { TextLink } from '../components/common/TextLink'
import { PurchaseOrderForm } from '../components/procurement/PurchaseOrderForm'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'
import { getErrorMessage } from '../services/api'
import { procurementService } from '../services/procurementService'
import { formatCurrency, formatDate, formatNumber, formatPrice } from '../utils/format'

type PendingAction = 'submit' | 'delete' | null

export default function ProcurementDetail() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const { hasPermission } = useAuth()
  const order = useApi(() => procurementService.getPurchaseOrder(id), [id])
  const [editing, setEditing] = useState(false)
  const [pendingAction, setPendingAction] = useState<PendingAction>(null)
  const [busy, setBusy] = useState(false)

  const po = order.data
  const canEdit = po?.status === 'Draft' && hasPermission('procurement:create')

  const runAction = async () => {
    if (!po || !pendingAction) return
    setBusy(true)
    try {
      if (pendingAction === 'submit') {
        await procurementService.submitForApproval(po.id)
        toast.success(`${po.id} submitted for approval.`)
        order.reload()
      } else {
        await procurementService.deleteDraft(po.id)
        toast.success(`${po.id} deleted.`)
        navigate('/procurement')
      }
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
      setPendingAction(null)
    }
  }

  return (
    <>
      <PageHeader
        title={`Purchase order ${id}`}
        back={{ to: '/procurement', label: 'Procurement' }}
        actions={
          canEdit && (
            <>
              <Button onClick={() => setEditing(true)}>
                <Pencil className="size-4" aria-hidden />
                Edit
              </Button>
              <Button onClick={() => setPendingAction('delete')}>
                <Trash2 className="size-4" aria-hidden />
                Delete
              </Button>
              <Button variant="primary" onClick={() => setPendingAction('submit')}>
                <Send className="size-4" aria-hidden />
                Submit for approval
              </Button>
            </>
          )
        }
      />

      <Card title="Order details">
        <QueryBoundary state={order} resource="purchase order">
          {(data) => (
            <>
              <DetailList
                items={[
                  { label: 'PO ID', value: data.id },
                  { label: 'Status', value: <StatusBadge status={data.status} /> },
                  { label: 'Created by', value: data.created_by },
                  {
                    label: 'Supplier',
                    value: hasPermission('suppliers:view') ? (
                      <TextLink to={`/suppliers/${data.supplier_id}`}>{data.supplier_name}</TextLink>
                    ) : (
                      data.supplier_name
                    ),
                  },
                  {
                    label: 'Product',
                    value: hasPermission('products:view') ? (
                      <TextLink to={`/products/${data.product_id}`}>{data.product_name}</TextLink>
                    ) : (
                      data.product_name
                    ),
                  },
                  { label: 'Quantity', value: formatNumber(data.quantity) },
                  { label: 'Unit price', value: formatPrice(data.unit_price) },
                  { label: 'Total amount', value: formatCurrency(data.total_amount) },
                  { label: 'Order date', value: formatDate(data.order_date) },
                  { label: 'Expected delivery', value: formatDate(data.expected_delivery) },
                  { label: 'Actual delivery', value: formatDate(data.actual_delivery) },
                  { label: 'Reason', value: data.reason || '—' },
                ]}
              />
              {data.status === 'Pending Approval' && hasPermission('procurement:approve') && (
                <p className="mt-5 border-t border-slate-200 pt-4 text-sm text-slate-600">
                  This order is waiting for a decision in the <TextLink to="/approvals">Approval Center</TextLink>.
                </p>
              )}
            </>
          )}
        </QueryBoundary>
      </Card>

      {editing && po && (
        <PurchaseOrderForm
          purchaseOrder={po}
          onClose={() => setEditing(false)}
          onSaved={() => {
            setEditing(false)
            order.reload()
          }}
        />
      )}

      {pendingAction === 'submit' && (
        <ConfirmDialog
          title="Submit for approval"
          message={`Submit ${id} for approval? It can no longer be edited once submitted.`}
          confirmLabel="Submit"
          busy={busy}
          onConfirm={runAction}
          onCancel={() => setPendingAction(null)}
        />
      )}
      {pendingAction === 'delete' && (
        <ConfirmDialog
          title="Delete draft"
          message={`Delete draft ${id}? This cannot be undone.`}
          confirmLabel="Delete"
          tone="danger"
          busy={busy}
          onConfirm={runAction}
          onCancel={() => setPendingAction(null)}
        />
      )}
    </>
  )
}
