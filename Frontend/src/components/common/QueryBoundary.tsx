import type { ReactNode } from 'react'

import type { ApiState } from '../../hooks/useApi'
import { ErrorState } from './ErrorState'
import { LoadingSpinner } from './LoadingSpinner'

interface QueryBoundaryProps<T> {
  state: ApiState<T>
  /** e.g. "inventory" -> "Loading inventory..." / "Unable to load inventory." */
  resource: string
  children: (data: T) => ReactNode
}

/** Renders the loading and error states for an API request, then the data. */
export function QueryBoundary<T>({ state, resource, children }: QueryBoundaryProps<T>) {
  if (state.error) {
    return <ErrorState message={`Unable to load ${resource}. ${state.error}`} onRetry={state.reload} />
  }
  if (state.data === null) return <LoadingSpinner label={`Loading ${resource}...`} />
  return (
    <div className={state.loading ? 'opacity-60 transition-opacity' : undefined} aria-busy={state.loading}>
      {children(state.data)}
    </div>
  )
}
