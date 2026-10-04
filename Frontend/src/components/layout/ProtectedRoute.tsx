import { ShieldAlert } from 'lucide-react'
import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import type { Permission } from '../../types'
import { LoadingSpinner } from '../common/LoadingSpinner'

/** Redirects unauthenticated users to /login. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, initializing } = useAuth()
  const location = useLocation()
  if (initializing) return <LoadingSpinner label="Restoring session..." />
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}

/** Shows an access-denied message when the user lacks a permission (the API would return 403 anyway). */
export function RequirePermission({ permission, children }: { permission: Permission; children: ReactNode }) {
  const { hasPermission } = useAuth()
  if (!hasPermission(permission)) {
    return (
      <div role="alert" className="flex flex-col items-center gap-2 py-20 text-center">
        <ShieldAlert className="size-8 text-slate-400" aria-hidden />
        <h1 className="text-lg font-semibold text-slate-900">Access denied</h1>
        <p className="text-sm text-slate-500">Your role does not have permission to view this page.</p>
      </div>
    )
  }
  return children
}
