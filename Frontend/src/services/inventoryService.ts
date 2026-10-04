import type { InventoryItem, InventoryStats } from '../types'
import { api, cleanParams } from './api'

export interface InventoryFilters {
  search?: string
  status?: string
  warehouse?: string
  product_id?: string
  [key: string]: string | undefined
}

export const inventoryService = {
  getInventory: (filters: InventoryFilters = {}) =>
    api.get<InventoryItem[]>('/inventory', { params: cleanParams(filters) }).then((r) => r.data),
  getItem: (id: string) => api.get<InventoryItem>(`/inventory/${encodeURIComponent(id)}`).then((r) => r.data),
  getStats: () => api.get<InventoryStats>('/inventory/stats').then((r) => r.data),
}
