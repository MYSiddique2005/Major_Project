export const SALES_STATUSES = ['Pending', 'Processing', 'Completed', 'Cancelled'] as const
export type SalesStatus = (typeof SALES_STATUSES)[number]

export interface Sale {
  id: string
  customer: string
  product_id: string
  product_name: string
  sku: string
  quantity: number
  unit_price: number
  total_amount: number
  order_date: string
  status: SalesStatus
}

export interface SalesStats {
  total_revenue: number
  total_orders: number
  average_order_value: number
  pending: number
  processing: number
  completed: number
  cancelled: number
}
