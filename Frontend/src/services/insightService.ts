import type { AiInsight, AiScan, PurchaseOrder } from '../types'
import { api, cleanParams } from './api'

/** A scan makes one model request, which can wait on the provider's rate limit. */
const SCAN_TIMEOUT_MS = 300_000

export const insightService = {
  list: (filters: { includePast?: boolean } = {}) =>
    api
      .get<AiInsight[]>('/ai/insights', { params: cleanParams({ include_past: filters.includePast ? 'true' : undefined }) })
      .then((r) => r.data),
  listScans: (limit = 5) => api.get<AiScan[]>('/ai/insights/scans', { params: { limit } }).then((r) => r.data),
  runScan: () => api.post<AiScan>('/ai/insights/scan', null, { timeout: SCAN_TIMEOUT_MS }).then((r) => r.data),
  acknowledge: (id: string) =>
    api.post<AiInsight>(`/ai/insights/${encodeURIComponent(id)}/acknowledge`).then((r) => r.data),
  draftOrder: (id: string) =>
    api.post<PurchaseOrder>(`/ai/insights/${encodeURIComponent(id)}/draft-order`).then((r) => r.data),
  dismiss: (id: string) => api.post<AiInsight>(`/ai/insights/${encodeURIComponent(id)}/dismiss`).then((r) => r.data),
}
