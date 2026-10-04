export const RISK_LEVELS = ['Critical', 'High', 'Medium', 'Low'] as const
export type RiskLevel = (typeof RISK_LEVELS)[number]

export type ForecastMethod = 'moving_average' | 'linear_trend'

/** Stockout risk for one product, produced by fixed rules (not AI). */
export interface StockRiskItem {
  product_id: string
  product_name: string
  sku: string
  category: string
  on_hand: number
  safety_stock: number
  reorder_level: number
  avg_daily_demand: number
  previous_avg_daily_demand: number
  demand_trend_pct: number | null
  days_of_cover: number | null
  projected_stockout_date: string | null
  supplier_id: string
  supplier_name: string
  lead_time_days: number
  lead_time_source: 'observed deliveries' | 'supplier master data'
  inbound_units: number
  next_inbound_date: string | null
  overdue_inbound_units: number
  awaiting_approval_units: number
  risk_level: RiskLevel
  drivers: string[]
  reorder_point: number
  suggested_order_quantity: number
  suggested_supplier_id: string | null
  suggested_supplier_name: string | null
}

export interface WeeklyDemand {
  week_start: string
  units: number
}

export interface DemandForecast {
  product_id: string
  product_name: string
  method: ForecastMethod
  method_selection: 'requested' | 'lowest backtest error'
  history: WeeklyDemand[]
  forecast: WeeklyDemand[]
  avg_weekly_forecast: number
  backtest_wape: Record<ForecastMethod, number | null>
}

export interface SupplierPerformanceItem {
  supplier_id: string
  supplier_name: string
  status: 'Active' | 'Inactive'
  orders_total: number
  deliveries_analyzed: number
  on_time_rate: number | null
  avg_delay_days: number | null
  max_delay_days: number | null
  avg_lead_time_days: number | null
  delay_trend: 'worsening' | 'improving' | 'stable' | 'insufficient data'
  open_orders: number
  overdue_orders: number
  risk_level: RiskLevel
  drivers: string[]
}

export interface RiskAlert {
  id: string
  category: 'Stockout Risk' | 'Supplier Risk'
  severity: RiskLevel
  title: string
  message: string
  entity: 'product' | 'supplier'
  entity_id: string
  source: string
}

export interface WhatIfRequest {
  product_id: string
  demand_change_pct: number
  lead_time_change_days: number
  order_quantity: number
  horizon_days: number
}

export interface WhatIfOutcome {
  daily_demand: number
  lead_time_days: number
  stockout_date: string | null
  days_until_stockout: number | null
  days_below_safety: number
  unmet_demand_units: number
  ending_stock: number
  points: { date: string; stock: number }[]
}

export interface WhatIfResult {
  product_id: string
  product_name: string
  on_hand: number
  safety_stock: number
  horizon_days: number
  baseline: WhatIfOutcome
  scenario: WhatIfOutcome
  assumptions: string[]
}
