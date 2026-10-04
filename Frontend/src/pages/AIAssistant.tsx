import { Info, Send, Sparkles } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent } from 'react'

import { Button } from '../components/common/Button'
import { PageHeader } from '../components/common/PageHeader'
import { getErrorMessage } from '../services/api'
import { aiService } from '../services/aiService'

interface Message {
  id: number
  author: 'user' | 'assistant'
  text: string
}

const SUGGESTED_QUESTIONS = [
  'Which products are at risk of stockout?',
  'Why is Product A at risk?',
  'Which suppliers have the most delivery delays?',
  'Which products should we reorder?',
]

const PLACEHOLDER_NOTICE = 'AI functionality is currently under development.'

export default function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const nextId = useRef(1)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'nearest' })
  }, [messages])

  const append = (author: Message['author'], text: string) =>
    setMessages((list) => [...list, { id: nextId.current++, author, text }])

  const send = async (text: string) => {
    const message = text.trim()
    if (!message || sending) return
    append('user', message)
    setInput('')
    setSending(true)
    try {
      // Phase 1: the backend returns a "not_implemented" placeholder; no LLM is called.
      const response = await aiService.chat(message)
      append('assistant', `${PLACEHOLDER_NOTICE} ${response.message}`)
    } catch (err) {
      append('assistant', getErrorMessage(err, 'Unable to reach the assistant endpoint.'))
    } finally {
      setSending(false)
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
          <strong className="font-semibold">Placeholder.</strong> LLM-powered enterprise reasoning will be integrated in a
          future development phase. Messages sent here receive a fixed response; no AI model is involved.
        </p>
      </div>

      <div className="flex h-[calc(100vh-19rem)] min-h-96 flex-col rounded-lg border border-slate-200 bg-white">
        <div className="flex-1 space-y-4 overflow-y-auto p-5" aria-live="polite">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <Sparkles className="size-7 text-slate-400" aria-hidden />
              <p className="mt-3 text-sm font-medium text-slate-900">Suggested questions</p>
              <p className="mt-1 text-xs text-slate-500">Examples of what the assistant will answer once it is built.</p>
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
                  className={`max-w-[80%] rounded-lg px-3.5 py-2.5 text-sm ${
                    message.author === 'user' ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-800'
                  }`}
                >
                  <p className={`mb-0.5 text-xs font-semibold ${message.author === 'user' ? 'text-blue-100' : 'text-slate-500'}`}>
                    {message.author === 'user' ? 'You' : 'IntelliERP · placeholder response'}
                  </p>
                  {message.text}
                </div>
              </div>
            ))
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
