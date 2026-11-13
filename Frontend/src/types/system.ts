export interface SystemInfo {
  app_name: string
  version: string
  /** The last completed build phase (9 of 9: the project is complete). */
  phase: number
  data_backend: 'postgres' | 'memory'
  persistent: boolean
  /** The day the analytics treat as today: the latest sales order date. */
  business_date: string
  ai_configured: boolean
  ai_provider: 'gemini' | 'anthropic'
  ai_model: string
  grounding: boolean
  verifier: 'patterns' | 'trace-rule' | 'trace' | 'off'
}
