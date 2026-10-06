export const AUDIT_STATUSES = ['SUCCESS', 'FAILED'] as const
export type AuditStatus = (typeof AUDIT_STATUSES)[number]

export const AUDIT_ACTIONS = [
  'LOGIN',
  'CREATE_PURCHASE_ORDER',
  'UPDATE_PURCHASE_ORDER',
  'DELETE_PURCHASE_ORDER',
  'SUBMIT_FOR_APPROVAL',
  'APPROVE_PURCHASE_ORDER',
  'REJECT_PURCHASE_ORDER',
  'AI_QUERY',
  'AI_SCAN',
  'REVIEW_AI_INSIGHT',
] as const

export interface AuditLog {
  id: string
  timestamp: string
  user_id: string
  username: string
  action: string
  entity: string
  entity_id: string
  status: AuditStatus
  description: string
}
