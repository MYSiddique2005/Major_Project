import axios, { AxiosError } from 'axios'

import { tokenStorage } from '../utils/tokenStorage'

/** Fired when the backend rejects our token so the auth state can reset. */
export const UNAUTHORIZED_EVENT = 'intellierp:unauthorized'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const isLoginRequest = error.config?.url?.endsWith('/auth/login')
    if (error.response?.status === 401 && !isLoginRequest) {
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }
    return Promise.reject(error)
  },
)

interface ValidationIssue {
  loc?: (string | number)[]
  msg: string
}

/** Turns any thrown value into a message that is safe to show to users. */
export function getErrorMessage(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (!axios.isAxiosError(error)) return fallback
  if (!error.response) return 'Unable to reach the server. Check that the backend is running.'
  const detail = (error.response.data as { detail?: string | ValidationIssue[] } | undefined)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((issue) => `${issue.loc?.at(-1) ?? 'field'}: ${issue.msg}`).join('; ')
  }
  if (error.response.status === 403) return 'You do not have permission to do that.'
  return fallback
}

/** Drops empty filter values so they are not sent as query parameters. */
export function cleanParams<T extends Record<string, string | undefined>>(params: T): Partial<T> {
  return Object.fromEntries(Object.entries(params).filter(([, value]) => value)) as Partial<T>
}
