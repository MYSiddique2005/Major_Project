import { AlertTriangle, BookOpen, Database, Info, Send, Sparkles } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'

import { RecommendationCard } from '../components/ai/RecommendationCard'
import { Button } from '../components/common/Button'
import { PageHeader } from '../components/common/PageHeader'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../services/api'
import { aiService } from '../services/aiService'
import type { ChatAction, ChatKnowledge, ChatSource, ChatTurn, Recommendation } from '../types'

interface Message {
  id: number
  author: 'user' | 'assistant'
  text: string
  sources?: ChatSource[]
  knowledge?: ChatKnowledge[]
  unverifiedFigures?: string[]
  recommendations?: Recommendation[]
  actions?: ChatAction[]
  /** Only real answers are sent back to the assistant as conversation history. */
  inHistory: boolean
}

const SUGGESTED_QUESTIONS = [
  'Which products are at risk of stockout?',
  'Which suppliers have the most delivery delays?',
  'Which products should we reorder, and how much?',
  'What happens to our most at-risk product if demand rises 20%?',
]

const TOOL_LABELS: Record<string, string> = {
  list_stock_risk: 'Stock risk list',
  get_stock_risk: 'Stock risk',
  get_demand_forecast: 'Demand forecast',
  list_supplier_performance: 'Supplier performance',
  list_risk_alerts: 'Risk alerts',
  run_what_if: 'What-if projection',
  search_products: 'Products',
  get_inventory: 'Inventory',
  get_sales_summary: 'Sales summary',
  list_purchase_orders: 'Purchase orders',
  list_suppliers: 'Suppliers',
  get_product_overview: 'Product overview',
  propose_recommendation: 'Recommendation check',
  draft_purchase_order: 'Draft purchase order',
  search_knowledge: 'Knowledge base search',
}

/** "Stock risk (P059)" - the tool's name plus the record it was asked about, when there is one. */
function sourceLabel(source: ChatSource): string {
  const label = TOOL_LABELS[source.tool] ?? source.tool
  const subject =
    source.input.product_id ??
    source.input.supplier_id ??
    source.input.subject_id ??
    source.input.search ??
    source.input.query
  return typeof subject === 'string' && subject ? `${label} (${subject})` : label
}

export default function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const { hasPermission } = useAuth()
  const canDraft = hasPermission('procurement:create')
  const nextId = useRef(1)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'nearest' })
  }, [messages])

  const append = (message: Omit<Message, 'id'>) =>
    setMessages((list) => [...list, { ...message, id: nextId.current++ }])

  const send = async (text: string) => {
    const message = text.trim()
    if (!message || sending) return
    const history: ChatTurn[] = messages
      .filter((entry) => entry.inHistory)
      .map((entry) => ({ role: entry.author, content: entry.text }))
    setInput('')
    setSending(true)
    try {
      const response = await aiService.chat(message, history)
      const answered = response.status === 'ok'
      append({ author: 'user', text: message, inHistory: answered })
      append({
        author: 'assistant',
        text: response.message,
        sources: response.sources,
        knowledge: response.knowledge,
        recommendations: response.recommendations,
        actions: response.actions,
        unverifiedFigures: response.unverified_figures,
        inHistory: answered,
      })
    } catch (err) {
      append({ author: 'user', text: message, inHistory: false })
      append({
        author: 'assistant',
        text: getErrorMessage(err, 'Unable to reach the assistant.'),
        inHistory: false,
      })
    } finally {
      setSending(false)
    }
  }

  // Drafts created from a recommendation card, keyed by "message id:card index".
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [draftingKey, setDraftingKey] = useState<string | null>(null)

  const draftOrder = async (key: string, recommendation: Recommendation) => {
    setDraftingKey(key)
    try {
      const order = await aiService.draftOrder(recommendation)
      setDrafts((current) => ({ ...current, [key]: order.id }))
    } catch (err) {
      append({ author: 'assistant', text: getErrorMessage(err, 'The draft could not be created.'), inHistory: false })
    } finally {
      setDraftingKey(null)
    }
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    void send(input)
  }

  return (
    <>
      <PageHeader title="IntelliERP AI Assistant" subtitle="Ask questions about your enterprise data." />

      <div className="mb-4 flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
        <Info className="mt-0.5 size-4 shrink-0" aria-hidden />
        <p>
          Answers are written by an AI model from data it reads through IntelliERP's own reports, limited to what your
          role can see. The only record it can create is a draft purchase order, when you ask for one; a draft orders
          nothing until it is reviewed, submitted and approved. Check the figures against the linked pages before acting.
        </p>
      </div>

      <div className="flex h-[calc(100vh-19rem)] min-h-96 flex-col rounded-lg border border-slate-200 bg-white">
        <div className="flex-1 space-y-4 overflow-y-auto p-5" aria-live="polite">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <Sparkles className="size-7 text-slate-400" aria-hidden />
              <p className="mt-3 text-sm font-medium text-slate-900">Suggested questions</p>
              <p className="mt-1 text-xs text-slate-500">Answers usually take under a minute.</p>
              <div className="mt-4 flex max-w-xl flex-wrap justify-center gap-2">
                {SUGGESTED_QUESTIONS.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => void send(question)}
                    className="rounded-full border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`flex ${message.author === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] whitespace-pre-wrap rounded-lg px-3.5 py-2.5 text-sm ${
                    message.author === 'user' ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-800'
                  }`}
                >
                  <p className={`mb-0.5 text-xs font-semibold ${message.author === 'user' ? 'text-blue-100' : 'text-slate-500'}`}>
                    {message.author === 'user' ? 'You' : 'IntelliERP assistant'}
                  </p>
                  {message.text}
                  {message.recommendations && message.recommendations.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {message.recommendations.map((recommendation, index) => {
                        const key = `${message.id}:${index}`
                        // A draft the assistant itself made for this product in the same answer.
                        const made = message.actions?.find((action) => action.product_id === recommendation.product_id)
                        return (
                          <RecommendationCard
                            key={index}
                            recommendation={recommendation}
                            draft={
                              canDraft
                                ? {
                                    onDraft: () => void draftOrder(key, recommendation),
                                    busy: draftingKey === key,
                                    purchaseOrderId: made?.purchase_order_id ?? drafts[key] ?? null,
                                  }
                                : undefined
                            }
                          />
                        )
                      })}
                    </div>
                  )}
                  {message.actions?.map((action) => (
                    <p key={action.purchase_order_id} className="mt-3 rounded-md border border-violet-200 bg-violet-50 px-3 py-2 text-violet-950">
                      Draft{' '}
                      <Link to={`/procurement/${action.purchase_order_id}`} className="font-semibold underline">
                        {action.purchase_order_id}
                      </Link>{' '}
                      created: {action.quantity.toLocaleString()} × {action.product_name} from {action.supplier_name}. Nothing is
                      ordered until it is reviewed, submitted and approved.
                    </p>
                  ))}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap items-center gap-1.5 border-t border-slate-200 pt-2 text-xs text-slate-500">
                      <Database className="size-3.5" aria-hidden />
                      <span>Data used:</span>
                      {message.sources.map((source, index) => (
                        <span
                          key={index}
                          className={`rounded-full border px-2 py-0.5 ${
                            source.ok ? 'border-slate-300 bg-white text-slate-700' : 'border-red-200 bg-red-50 text-red-700'
                          }`}
                        >
                          {sourceLabel(source)}
                        </span>
                      ))}
                    </div>
                  )}
                  {message.unverifiedFigures && message.unverifiedFigures.length > 0 && (
                    <p role="note" className="mt-2 flex items-start gap-1.5 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1.5 text-xs text-amber-900">
                      <AlertTriangle className="mt-0.5 size-3.5 shrink-0" aria-hidden />
                      <span>
                        Not found in the system data: {message.unverifiedFigures.join(', ')}. The assistant may have
                        worked {message.unverifiedFigures.length === 1 ? 'this figure' : 'these figures'} out itself; check before relying on{' '}
                        {message.unverifiedFigures.length === 1 ? 'it' : 'them'}.
                      </span>
                    </p>
                  )}
                  {message.knowledge && message.knowledge.length > 0 && (
                    <div className="mt-2 flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
                      <BookOpen className="size-3.5" aria-hidden />
                      <span>Company rules consulted:</span>
                      {message.knowledge.map((entry) => (
                        <span key={entry.id} className="rounded-full border border-slate-300 bg-white px-2 py-0.5 text-slate-700">
                          {entry.title}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {sending && (
            <p className="text-sm text-slate-500">
              Reading the ERP data… This can take a minute or two when the free model tier is busy.
            </p>
          )}
          <div ref={endRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 p-3">
          <input
            className="field"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask a question about sales, inventory or procurement"
            aria-label="Message"
            maxLength={2000}
          />
          <Button type="submit" variant="primary" disabled={sending || !input.trim()}>
            <Send className="size-4" aria-hidden />
            Send
          </Button>
        </form>
      </div>
    </>
  )
}
