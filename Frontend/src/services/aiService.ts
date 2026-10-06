import type { ChatResponse, ChatTurn } from '../types'
import { api } from './api'

/**
 * The assistant can take a while: it may call several ERP tools before it answers, and on a free
 * model tier it waits when the provider's per-minute request limit is reached.
 */
const CHAT_TIMEOUT_MS = 300_000

export const aiService = {
  chat: (message: string, history: ChatTurn[] = []) =>
    api.post<ChatResponse>('/ai/chat', { message, history }, { timeout: CHAT_TIMEOUT_MS }).then((r) => r.data),
}
