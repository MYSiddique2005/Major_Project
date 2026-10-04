import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

export function TextLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link to={to} className="font-medium text-brand-700 hover:underline">
      {children}
    </Link>
  )
}
