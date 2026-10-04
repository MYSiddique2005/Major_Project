import type { PurchaseOrder } from './procurement'

export const APPROVAL_STATUSES = ['Pending', 'Approved', 'Rejected'] as const
export type ApprovalStatus = (typeof APPROVAL_STATUSES)[number]

export interface Approval {
  id: string
  purchase_order_id: string
  purchase_order: PurchaseOrder
  requested_by: string
  requested_at: string
  reason: string
  status: ApprovalStatus
  decided_by: string | null
  decided_at: string | null
  comment: string | null
}
