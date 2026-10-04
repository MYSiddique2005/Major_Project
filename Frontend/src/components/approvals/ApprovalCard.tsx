import { Link } from 'react-router-dom'

import type { Approval } from '../../types'
import { formatCurrency, formatDateTime, formatNumber } from '../../utils/format'
import { Button } from '../common/Button'
import { StatusBadge } from '../common/StatusBadge'

interface ApprovalCardProps {
  approval: Approval
  onApprove: (approval: Approval) => void
  onReject: (approval: Approval) => void
}

export function ApprovalCard({ approval, onApprove, onReject }: ApprovalCardProps) {
  const po = approval.purchase_order
  const fields = [
    { label: 'Supplier', value: po.supplier_name },
    { label: 'Product', value: po.product_name },
    { label: 'Quantity', value: formatNumber(po.quantity) },
    { label: 'Total', value: formatCurrency(po.total_amount) },
    { label: 'Requested by', value: approval.requested_by },
    { label: 'Requested', value: formatDateTime(approval.requested_at) },
  ]

  return (
    <article className="rounded-lg border border-slate-200 bg-white">
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 px-5 py-3">
        <div>
          <p className="text-xs text-slate-500">Purchase order draft · {approval.id}</p>
          <h2 className="text-sm font-semibold text-slate-900">{po.id}</h2>
        </div>
        <StatusBadge status={approval.status === 'Pending' ? 'Pending Approval' : approval.status} />
      </header>
      <div className="px-5 py-4">
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-3">
          {fields.map((field) => (
            <div key={field.label}>
              <dt className="text-xs text-slate-500">{field.label}</dt>
              <dd className="text-sm text-slate-900">{field.value}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-3 text-sm text-slate-600">
          <span className="font-medium text-slate-700">Reason:</span> {approval.reason || 'No reason given'}
        </p>
        {approval.decided_by && (
          <p className="mt-1 text-sm text-slate-600">
            <span className="font-medium text-slate-700">{approval.status} by:</span> {approval.decided_by} on{' '}
            {formatDateTime(approval.decided_at)}
            {approval.comment && ` — “${approval.comment}”`}
          </p>
        )}
      </div>
      <footer className="flex flex-wrap items-center gap-2 border-t border-slate-200 px-5 py-3">
        {approval.status === 'Pending' && (
          <>
            <Button variant="primary" onClick={() => onApprove(approval)}>
              Approve
            </Button>
            <Button onClick={() => onReject(approval)}>Reject</Button>
          </>
        )}
        <Link to={`/procurement/${po.id}`} className="ml-auto text-sm font-medium text-brand-700 hover:underline">
          View details
        </Link>
      </footer>
    </article>
  )
}
