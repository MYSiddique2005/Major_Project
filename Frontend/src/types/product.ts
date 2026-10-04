import type { StockStatus } from './inventory'

export const PRODUCT_STATUSES = ['Active', 'Discontinued'] as const
export type ProductStatus = (typeof PRODUCT_STATUSES)[number]

export interface Product {
  id: string
  sku: string
  name: string
  category: string
  supplier_id: string
  supplier_name: string
  price: number
  unit_cost: number
  current_stock: number
  reorder_level: number
  stock_status: StockStatus
  status: ProductStatus
}
