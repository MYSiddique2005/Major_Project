import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { Button } from '../components/common/Button'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../services/api'

/** Development/demo accounts only - documented in the README; replace before production. */
const DEMO_ACCOUNTS = [
  { username: 'admin', password: 'admin123', role: 'Admin' },
  { username: 'inventory', password: 'inventory123', role: 'Inventory Manager' },
  { username: 'procurement', password: 'procurement123', role: 'Procurement Manager' },
  { username: 'employee', password: 'employee123', role: 'Employee' },
]

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const destination = (location.state as { from?: string } | null)?.from ?? '/dashboard'
  if (user) return <Navigate to={destination} replace />

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await login(username, password)
      navigate(destination, { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, 'Unable to sign in.'))
      setSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center justify-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-md bg-brand-600 text-sm font-bold text-white">IE</span>
          <span className="text-xl font-semibold text-slate-900">IntelliERP</span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
          <h1 className="text-base font-semibold text-slate-900">Sign in to your account</h1>
          {error && (
            <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
              {error}
            </p>
          )}
          <div>
            <label htmlFor="username" className="field-label">
              Username
            </label>
            <input
              id="username"
              className="field"
              autoComplete="username"
              required
              autoFocus
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="password" className="field-label">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="field"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          <Button type="submit" variant="primary" className="w-full" disabled={submitting}>
            {submitting ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>

        <div className="mt-4 rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-xs font-semibold tracking-wide text-slate-600 uppercase">Demo accounts (development only)</p>
          <ul className="mt-2 space-y-1">
            {DEMO_ACCOUNTS.map((account) => (
              <li key={account.username}>
                <button
                  type="button"
                  onClick={() => {
                    setUsername(account.username)
                    setPassword(account.password)
                  }}
                  className="flex w-full items-center justify-between rounded px-2 py-1 text-left text-sm hover:bg-slate-100"
                >
                  <span className="text-slate-700">{account.role}</span>
                  <code className="text-xs text-slate-500">
                    {account.username} / {account.password}
                  </code>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  )
}
