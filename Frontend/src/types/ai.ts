/** One tool call the assistant made to answer a question. */
export interface ChatSource {
  tool: string
  input: Record<string, unknown>
  ok: boolean
}

/** A knowledge-base passage (a company definition or rule) given to the assistant for a question. */
export interface ChatKnowledge {
  id: string
  title: string
  category: string
  score: number
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

/** Contract of POST /ai/chat. `status` is "ok", "not_configured", "refused" or "incomplete". */
export interface ChatResponse {
  status: string
  message: string
  sources: ChatSource[]
  knowledge: ChatKnowledge[]
  recommendations: unknown[]
  actions: unknown[]
  provider: string | null
  model: string | null
  usage: Record<string, number> | null
}
