import type { PurchaseOrder, PurchaseOrderInput } from '../types'
import { api, cleanParams } from './api'

export interface ProcurementFilters {
  search?: string
  status?: string
  supplier_id?: string
  product_id?: string
  [key: string]: string | undefined
}

const path = (id: string) => `/procurement/${encodeURIComponent(id)}`

export const procurementService = {
  getPurchaseOrders: (filters: ProcurementFilters = {}) =>
    api.get<PurchaseOrder[]>('/procurement', { params: cleanParams(filters) }).then((r) => r.data),
  getPurchaseOrder: (id: string) => api.get<PurchaseOrder>(path(id)).then((r) => r.data),
  createDraft: (input: PurchaseOrderInput) => api.post<PurchaseOrder>('/procurement', input).then((r) => r.data),
  updateDraft: (id: string, input: Partial<PurchaseOrderInput>) =>
    api.put<PurchaseOrder>(path(id), input).then((r) => r.data),
  deleteDraft: (id: string) => api.delete<void>(path(id)).then(() => undefined),
  submitForApproval: (id: string) => api.post<PurchaseOrder>(`${path(id)}/submit`).then((r) => r.data),
}
