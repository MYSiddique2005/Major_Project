import { Inbox } from 'lucide-react'

export function EmptyState({ message = 'No records found.' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-sm text-slate-500">
      <Inbox className="size-6 text-slate-400" aria-hidden />
      {message}
    </div>
  )
}
