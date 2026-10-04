export const SUPPLIER_STATUSES = ['Active', 'Inactive'] as const
export type SupplierStatus = (typeof SUPPLIER_STATUSES)[number]

export interface SuppliedProduct {
  id: string
  name: string
  sku: string
}

export interface Supplier {
  id: string
  name: string
  contact_name: string
  email: string
  phone: string
  country: string
  products_supplied: SuppliedProduct[]
  avg_delivery_days: number
  delivery_reliability: number
  status: SupplierStatus
}
