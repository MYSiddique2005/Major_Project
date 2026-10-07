export interface SystemInfo {
  app_name: string
  phase: number
  data_backend: 'postgres' | 'memory'
  persistent: boolean
  /** The day the analytics treat as today: the latest sales order date. */
  business_date: string
}
