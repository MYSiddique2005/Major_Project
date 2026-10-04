export interface SystemInfo {
  app_name: string
  phase: number
  data_backend: 'postgres' | 'memory'
  persistent: boolean
}
