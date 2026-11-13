import { Menu } from 'lucide-react'
import { Link } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import { useApi } from '../../hooks/useApi'
import { systemService } from '../../services/systemService'
import { formatDate, formatRole } from '../../utils/format'

export function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  const { user } = useAuth()
  const system = useApi(systemService.getInfo, [])
  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 sm:px-6">
      <div className="flex items-center gap-3">
        <button type="button" onClick={onMenuClick} className="rounded p-1.5 text-slate-600 hover:bg-slate-100 lg:hidden" aria-label="Open menu">
          <Menu className="size-5" aria-hidden />
        </button>
        {system.data && (
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            v{system.data.version} ·{' '}
            {system.data.persistent ? 'PostgreSQL, data is saved' : 'in-memory demo data, resets on server restart'}
            {' · '}data as of {formatDate(system.data.business_date)}
          </span>
        )}
      </div>
      {user && (
        <Link to="/settings" className="flex items-center gap-2.5 rounded-md px-2 py-1 hover:bg-slate-100">
          <span className="hidden text-right sm:block">
            <span className="block text-sm leading-tight font-medium text-slate-900">{user.full_name}</span>
            <span className="block text-xs leading-tight text-slate-500">{formatRole(user.role)}</span>
          </span>
          <span className="flex size-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700" aria-hidden>
            {user.full_name
              .split(' ')
              .map((part) => part[0])
              .join('')
              .slice(0, 2)}
          </span>
        </Link>
      )}
    </header>
  )
}
