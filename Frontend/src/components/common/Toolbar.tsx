import type { ReactNode } from 'react'

/** Row of search / filter controls above a table. */
export function Toolbar({ children }: { children: ReactNode }) {
  return <div className="flex flex-col gap-3 border-b border-slate-200 p-4 sm:flex-row sm:items-center">{children}</div>
}
