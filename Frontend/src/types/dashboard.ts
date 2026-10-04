export interface DashboardSummary {
  total_sales: number
  total_orders: number
  inventory_items: number
  low_stock_items: number
  critical_stock_items: number
  out_of_stock_items: number
  pending_purchase_orders: number
  active_suppliers: number
}

export interface SalesTrendPoint {
  month: string
  label: string
  revenue: number
  orders: number
}

export interface StatusCount {
  status: string
  count: number
}
