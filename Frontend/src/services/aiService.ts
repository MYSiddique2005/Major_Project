import type { ChatResponse } from '../types'
import { api } from './api'

/**
 * Placeholder AI contract. The backend does not call an LLM yet; when it does,
 * this call and its response type stay the same.
 */
export const aiService = {
  chat: (message: string) => api.post<ChatResponse>('/ai/chat', { message }).then((r) => r.data),
}
