import { useState } from 'react'

import { ApprovalCard } from '../components/approvals/ApprovalCard'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { EmptyState } from '../components/common/EmptyState'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'
import { getErrorMessage } from '../services/api'
import { approvalService } from '../services/approvalService'
import { APPROVAL_STATUSES, type Approval } from '../types'

interface Decision {
  approval: Approval
  approve: boolean
}

export default function Approvals() {
  const toast = useToast()
  const [status, setStatus] = useState<string>('Pending')
  const [decision, setDecision] = useState<Decision | null>(null)
  const [comment, setComment] = useState('')
  const [busy, setBusy] = useState(false)
  const approvals = useApi(() => approvalService.getApprovals(status), [status])

  const openDecision = (approval: Approval, approve: boolean) => {
    setComment('')
    setDecision({ approval, approve })
  }

  const confirmDecision = async () => {
    if (!decision) return
    const { approval, approve } = decision
    setBusy(true)
    try {
      await (approve ? approvalService.approve(approval.id, comment) : approvalService.reject(approval.id, comment))
      toast.success(`${approval.purchase_order_id} ${approve ? 'approved' : 'rejected'}.`)
      approvals.reload()
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
      setDecision(null)
    }
  }

  return (
    <>
      <PageHeader
        title="Approval Center"
        subtitle="Purchase orders only take effect after a person approves them here."
        actions={<FilterDropdown label="Statuses" value={status} options={APPROVAL_STATUSES} onChange={setStatus} />}
      />

      <QueryBoundary state={approvals} resource="approvals">
        {(rows) =>
          rows.length === 0 ? (
            <div className="rounded-lg border border-slate-200 bg-white">
              <EmptyState message={status === 'Pending' ? 'Nothing is waiting for approval.' : 'No approvals found.'} />
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              {rows.map((approval) => (
                <ApprovalCard
                  key={approval.id}
                  approval={approval}
                  onApprove={(a) => openDecision(a, true)}
                  onReject={(a) => openDecision(a, false)}
                />
              ))}
            </div>
          )
        }
      </QueryBoundary>

      {decision && (
        <ConfirmDialog
          title={decision.approve ? 'Approve purchase order' : 'Reject purchase order'}
          message={`${decision.approve ? 'Approve' : 'Reject'} ${decision.approval.purchase_order_id}: ${decision.approval.purchase_order.quantity} × ${decision.approval.purchase_order.product_name} from ${decision.approval.purchase_order.supplier_name}?`}
          confirmLabel={decision.approve ? 'Approve' : 'Reject'}
          tone={decision.approve ? 'primary' : 'danger'}
          busy={busy}
          onConfirm={confirmDecision}
          onCancel={() => setDecision(null)}
        >
          <label htmlFor="decision-comment" className="field-label">
            Comment (optional)
          </label>
          <textarea
            id="decision-comment"
            rows={2}
            maxLength={500}
            className="field"
            value={comment}
            onChange={(event) => setComment(event.target.value)}
          />
        </ConfirmDialog>
      )}
    </>
  )
}
