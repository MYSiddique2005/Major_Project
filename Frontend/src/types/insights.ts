import type { RiskLevel } from './analytics'

export type RecommendationAction = 'reorder' | 'expedite_delivery' | 'review_supplier' | 'monitor'

export interface EvidenceItem {
  module: 'sales' | 'inventory' | 'procurement' | 'supplier' | 'rule'
  statement: string
}

/** What the server found when it checked the model's text against its own figures and rules. */
export interface RecommendationChecks {
  modules_cited: string[]
  cross_module: boolean
  quantity_matches_rule: boolean | null
  supplier_supplies_product: boolean | null
  figures_checked: number
  figures_unmatched: string[]
}

/** A recommendation from the AI assistant, in the chat or from a scan. */
export interface Recommendation {
  subject_type: 'product' | 'supplier'
  subject_id: string
  subject_name: string
  severity: RiskLevel
  headline: string
  explanation: string
  action: RecommendationAction
  product_id: string | null
  product_name: string | null
  supplier_id: string | null
  supplier_name: string | null
  quantity: number | null
  system_quantity: number | null
  evidence: EvidenceItem[]
  checks: RecommendationChecks
}

export const INSIGHT_STATUSES = ['New', 'Acknowledged', 'Dismissed', 'Superseded'] as const
export type InsightStatus = (typeof INSIGHT_STATUSES)[number]

export interface AiInsight extends Recommendation {
  id: string
  scan_id: string
  created_at: string
  status: InsightStatus
  reviewed_by: string | null
  reviewed_at: string | null
}

export interface AiScan {
  id: string
  started_at: string
  finished_at: string | null
  trigger: string
  status: 'Running' | 'Completed' | 'Failed'
  findings: number
  insights: number
  message: string
  provider: string | null
  model: string | null
}
