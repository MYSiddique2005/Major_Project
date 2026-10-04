import { AlertTriangle } from 'lucide-react'

import { Button } from './Button'

interface ErrorStateProps {
  message?: string
  onRetry?: () => void
}

export function ErrorState({ message = 'Unable to load data.', onRetry }: ErrorStateProps) {
  return (
    <div role="alert" className="flex flex-col items-center justify-center gap-3 py-12 text-sm text-slate-600">
      <AlertTriangle className="size-6 text-red-500" aria-hidden />
      <p>{message}</p>
      {onRetry && <Button onClick={onRetry}>Try again</Button>}
    </div>
  )
}
