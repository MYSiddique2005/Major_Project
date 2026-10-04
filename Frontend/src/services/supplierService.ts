import type { Supplier } from '../types'
import { api, cleanParams } from './api'

export interface SupplierFilters {
  search?: string
  status?: string
  [key: string]: string | undefined
}

export const supplierService = {
  getSuppliers: (filters: SupplierFilters = {}) =>
    api.get<Supplier[]>('/suppliers', { params: cleanParams(filters) }).then((r) => r.data),
  getSupplier: (id: string) => api.get<Supplier>(`/suppliers/${encodeURIComponent(id)}`).then((r) => r.data),
}
