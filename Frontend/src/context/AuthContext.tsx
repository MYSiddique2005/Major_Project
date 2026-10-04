import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { UNAUTHORIZED_EVENT } from '../services/api'
import { authService } from '../services/authService'
import type { Permission, User } from '../types'
import { tokenStorage } from '../utils/tokenStorage'

interface AuthContextValue {
  user: User | null
  /** True while the stored token is being verified on startup. */
  initializing: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  /** UX only - the backend enforces permissions on every request. */
  hasPermission: (permission: Permission) => boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [initializing, setInitializing] = useState(() => tokenStorage.get() !== null)

  const logout = useCallback(() => {
    tokenStorage.clear()
    setUser(null)
  }, [])

  useEffect(() => {
    if (!tokenStorage.get()) return
    authService
      .getCurrentUser()
      .then(setUser)
      .catch(() => tokenStorage.clear())
      .finally(() => setInitializing(false))
  }, [])

  useEffect(() => {
    window.addEventListener(UNAUTHORIZED_EVENT, logout)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, logout)
  }, [logout])

  const login = useCallback(async (username: string, password: string) => {
    const response = await authService.login(username, password)
    tokenStorage.set(response.access_token)
    setUser(response.user)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      initializing,
      login,
      logout,
      hasPermission: (permission) => user?.permissions.includes(permission) ?? false,
    }),
    [user, initializing, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
