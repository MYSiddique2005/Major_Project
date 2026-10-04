export const STOCK_STATUSES = ['In Stock', 'Low Stock', 'Critical', 'Out of Stock'] as const
export type StockStatus = (typeof STOCK_STATUSES)[number]

export interface InventoryItem {
  id: string
  product_id: string
  product_name: string
  sku: string
  warehouse: string
  current_stock: number
  safety_stock: number
  reorder_level: number
  status: StockStatus
  last_updated: string
}

export interface InventoryStats {
  total_items: number
  total_units: number
  in_stock: number
  low_stock: number
  critical: number
  out_of_stock: number
}
