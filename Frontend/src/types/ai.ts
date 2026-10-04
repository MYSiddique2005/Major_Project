/** Contract of POST /ai/chat. Currently always returns status "not_implemented". */
export interface ChatResponse {
  status: string
  message: string
  sources: unknown[]
  recommendations: unknown[]
  actions: unknown[]
}
