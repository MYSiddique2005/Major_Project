import { useCallback, useEffect, useRef, useState, type DependencyList } from 'react'

import { getErrorMessage } from '../services/api'

export interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  reload: () => void
}

/**
 * Runs an async fetcher on mount and whenever `deps` change. Keeps the previous
 * data visible while refetching and ignores responses from superseded requests.
 */
export function useApi<T>(fetcher: () => Promise<T>, deps: DependencyList): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const requestId = useRef(0)

  useEffect(() => {
    const id = ++requestId.current
    setLoading(true)
    setError(null)
    fetcher()
      .then((result) => {
        if (id === requestId.current) setData(result)
      })
      .catch((err: unknown) => {
        if (id === requestId.current) setError(getErrorMessage(err))
      })
      .finally(() => {
        if (id === requestId.current) setLoading(false)
      })
    // The fetcher is intentionally re-created each render; `deps` controls refetching.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, reloadKey])

  const reload = useCallback(() => setReloadKey((key) => key + 1), [])
  return { data, loading, error, reload }
}
