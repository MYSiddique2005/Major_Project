import type { ChatResponse, ChatTurn, PurchaseOrder, Recommendation } from '../types'
import { api } from './api'

/**
 * The assistant can take a while: it may call several ERP tools before it answers, and on a free
 * model tier it waits when the provider's per-minute request limit is reached.
 */
const CHAT_TIMEOUT_MS = 300_000

/** The fields of a recommendation the server needs to check it again and draft the order. */
const proposalOf = (r: Recommendation) => ({
  subject_type: r.subject_type,
  subject_id: r.subject_id,
  headline: r.headline,
  explanation: r.explanation,
  action: r.action,
  product_id: r.product_id,
  supplier_id: r.supplier_id,
  quantity: r.quantity,
  evidence: r.evidence,
})

export const aiService = {
  draftOrder: (recommendation: Recommendation) =>
    api.post<PurchaseOrder>('/ai/recommendations/draft-order', proposalOf(recommendation)).then((r) => r.data),
  chat: (message: string, history: ChatTurn[] = []) =>
    api.post<ChatResponse>('/ai/chat', { message, history }, { timeout: CHAT_TIMEOUT_MS }).then((r) => r.data),
}
