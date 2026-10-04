import type { Sale, SalesStats } from '../types'
import { api, cleanParams } from './api'

export interface SalesFilters {
  search?: string
  status?: string
  product_id?: string
  [key: string]: string | undefined
}

export const salesService = {
  getSales: (filters: SalesFilters = {}) =>
    api.get<Sale[]>('/sales', { params: cleanParams(filters) }).then((r) => r.data),
  getSale: (id: string) => api.get<Sale>(`/sales/${encodeURIComponent(id)}`).then((r) => r.data),
  getStats: () => api.get<SalesStats>('/sales/stats').then((r) => r.data),
}
