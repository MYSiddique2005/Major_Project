import type { EvidenceItem, RecommendationChecks } from './insights'

export const PURCHASE_ORDER_STATUSES = [
  'Draft',
  'Pending Approval',
  'Approved',
  'Rejected',
  'Ordered',
  'Delivered',
  'Cancelled',
] as const
export type PurchaseOrderStatus = (typeof PURCHASE_ORDER_STATUSES)[number]

export type PurchaseOrderOrigin = 'Manual' | 'AI Assistant' | 'AI Insight'

/** The AI recommendation a draft was made from, as it stood then, with the server's checks on it. */
export interface KeptRecommendation {
  headline: string
  explanation: string
  severity: string
  system_quantity: number | null
  evidence: EvidenceItem[]
  checks: RecommendationChecks
  model: string | null
  requested_by: string
}

export interface PurchaseOrder {
  id: string
  supplier_id: string
  supplier_name: string
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_amount: number
  order_date: string
  expected_delivery: string
  actual_delivery: string | null
  status: PurchaseOrderStatus
  reason: string
  created_by: string
  origin: PurchaseOrderOrigin
  origin_ref: string | null
  ai_recommendation: KeptRecommendation | null
}

export interface PurchaseOrderInput {
  supplier_id: string
  product_id: string
  quantity: number
  unit_price?: number
  expected_delivery?: string
  reason?: string
}
