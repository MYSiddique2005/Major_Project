import type { DashboardSummary, SalesTrendPoint, StatusCount } from '../types'
import { api } from './api'

export const dashboardService = {
  getSummary: () => api.get<DashboardSummary>('/dashboard/summary').then((r) => r.data),
  getSalesTrend: () => api.get<SalesTrendPoint[]>('/dashboard/sales-trend').then((r) => r.data),
  getInventoryStatus: () => api.get<StatusCount[]>('/dashboard/inventory-status').then((r) => r.data),
  getProcurementStatus: () => api.get<StatusCount[]>('/dashboard/procurement-status').then((r) => r.data),
}
