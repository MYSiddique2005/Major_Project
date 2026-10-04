import { LogOut, X } from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import { formatRole } from '../../utils/format'
import { NAV_ITEMS } from './navigation'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const { user, logout, hasPermission } = useAuth()
  const items = NAV_ITEMS.filter((item) => !item.permission || hasPermission(item.permission))

  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-slate-900/40 lg:hidden" onClick={onClose} aria-hidden />}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-60 flex-col bg-slate-900 text-slate-300 transition-transform lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex h-14 items-center justify-between px-5">
          <div className="flex items-center gap-2.5">
            <span className="flex size-7 items-center justify-center rounded-md bg-brand-600 text-xs font-bold text-white">
              IE
            </span>
            <span className="text-base font-semibold text-white">IntelliERP</span>
          </div>
          <button type="button" onClick={onClose} className="rounded p-1 text-slate-400 hover:text-white lg:hidden" aria-label="Close menu">
            <X className="size-5" aria-hidden />
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-3" aria-label="Main">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? 'bg-slate-800 text-white' : 'hover:bg-slate-800/60 hover:text-white'
                }`
              }
            >
              <Icon className="size-4 shrink-0" aria-hidden />
              {label}
            </NavLink>
          ))}
        </nav>

        {user && (
          <div className="border-t border-slate-800 p-4">
            <p className="truncate text-sm font-medium text-white">{user.full_name}</p>
            <p className="truncate text-xs text-slate-400">{formatRole(user.role)}</p>
            <button
              type="button"
              onClick={logout}
              className="mt-3 flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white"
            >
              <LogOut className="size-4" aria-hidden />
              Log out
            </button>
          </div>
        )}
      </aside>
    </>
  )
}
