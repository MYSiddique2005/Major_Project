import type { Recommendation } from './insights'

/** One tool call the assistant made to answer a question. */
export interface ChatSource {
  tool: string
  input: Record<string, unknown>
  ok: boolean
}

/** A knowledge-base passage (a company definition or rule) given to the assistant for a question. */
export interface ChatKnowledge {
  id: string
  title: string
  category: string
  score: number
}

/** Something the assistant did at the user's request. Only one kind exists: a draft purchase order. */
export interface ChatAction {
  type: 'purchase_order_draft'
  purchase_order_id: string
  status: string
  product_id: string
  product_name: string
  supplier_id: string
  supplier_name: string
  quantity: number
  total_amount: number
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

/** Contract of POST /ai/chat. `status` is "ok", "not_configured", "refused" or "incomplete". */
export interface ChatResponse {
  status: string
  message: string
  sources: ChatSource[]
  knowledge: ChatKnowledge[]
  recommendations: Recommendation[]
  actions: ChatAction[]
  /** Figures in the answer that the server found in no tool result, knowledge passage or question. */
  unverified_figures: string[]
  provider: string | null
  model: string | null
  usage: Record<string, number> | null
}
