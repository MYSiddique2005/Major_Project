import type { ChatResponse, ChatTurn } from '../types'
import { api } from './api'

/** The assistant can take a while: it may call several ERP tools before it answers. */
const CHAT_TIMEOUT_MS = 180_000

export const aiService = {
  chat: (message: string, history: ChatTurn[] = []) =>
    api.post<ChatResponse>('/ai/chat', { message, history }, { timeout: CHAT_TIMEOUT_MS }).then((r) => r.data),
}
