import type {
  DemandForecast,
  ForecastMethod,
  RiskAlert,
  StockRiskItem,
  SupplierPerformanceItem,
  WhatIfRequest,
  WhatIfResult,
} from '../types'
import { api, cleanParams } from './api'

export const analyticsService = {
  getStockRisk: (filters: { level?: string; search?: string } = {}) =>
    api.get<StockRiskItem[]>('/analytics/stock-risk', { params: cleanParams(filters) }).then((r) => r.data),
  getProductRisk: (productId: string) =>
    api.get<StockRiskItem>(`/analytics/stock-risk/${encodeURIComponent(productId)}`).then((r) => r.data),
  getForecast: (productId: string, method?: ForecastMethod) =>
    api
      .get<DemandForecast>(`/analytics/forecast/${encodeURIComponent(productId)}`, { params: cleanParams({ method }) })
      .then((r) => r.data),
  getSupplierPerformance: () =>
    api.get<SupplierPerformanceItem[]>('/analytics/supplier-performance').then((r) => r.data),
  getAlerts: () => api.get<RiskAlert[]>('/analytics/alerts').then((r) => r.data),
  runWhatIf: (request: WhatIfRequest) => api.post<WhatIfResult>('/analytics/what-if', request).then((r) => r.data),
}
