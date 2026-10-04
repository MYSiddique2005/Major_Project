import type { Product } from '../types'
import { api, cleanParams } from './api'

export interface ProductFilters {
  search?: string
  category?: string
  status?: string
  [key: string]: string | undefined
}

export const productService = {
  getProducts: (filters: ProductFilters = {}) =>
    api.get<Product[]>('/products', { params: cleanParams(filters) }).then((r) => r.data),
  getProduct: (id: string) => api.get<Product>(`/products/${encodeURIComponent(id)}`).then((r) => r.data),
}
