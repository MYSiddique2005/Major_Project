import { useEffect, useState, type ReactNode } from 'react'

import { EmptyState } from './EmptyState'
import { Pagination } from './Pagination'

export interface Column<T> {
  header: string
  render: (row: T) => ReactNode
  align?: 'left' | 'right'
  /** Extra classes for the cells in this column. */
  className?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  rowKey: (row: T) => string
  onRowClick?: (row: T) => void
  pageSize?: number
  emptyMessage?: string
  caption: string
}

/** Generic table with client-side pagination, shared by every list page. */
export function DataTable<T>({
  columns,
  rows,
  rowKey,
  onRowClick,
  pageSize = 10,
  emptyMessage,
  caption,
}: DataTableProps<T>) {
  const [page, setPage] = useState(1)
  const pageCount = Math.max(1, Math.ceil(rows.length / pageSize))

  // Filters can shrink the result set below the current page.
  useEffect(() => {
    if (page > pageCount) setPage(1)
  }, [page, pageCount])

  if (rows.length === 0) return <EmptyState message={emptyMessage} />

  const visible = rows.slice((page - 1) * pageSize, page * pageSize)

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">{caption}</caption>
          <thead className="border-b border-slate-200 bg-slate-50 text-xs font-medium tracking-wide text-slate-500 uppercase">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.header}
                  scope="col"
                  className={`px-4 py-2.5 whitespace-nowrap ${column.align === 'right' ? 'text-right' : ''}`}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {visible.map((row) => (
              <tr
                key={rowKey(row)}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                onKeyDown={
                  onRowClick
                    ? (event) => {
                        if (event.key === 'Enter') onRowClick(row)
                      }
                    : undefined
                }
                tabIndex={onRowClick ? 0 : undefined}
                className={onRowClick ? 'cursor-pointer hover:bg-slate-50 focus-visible:bg-slate-50' : undefined}
              >
                {columns.map((column) => (
                  <td
                    key={column.header}
                    className={`px-4 py-2.5 text-slate-700 ${column.align === 'right' ? 'text-right tabular-nums' : ''} ${column.className ?? ''}`}
                  >
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > pageSize && (
        <Pagination page={page} pageSize={pageSize} total={rows.length} onPageChange={setPage} />
      )}
    </div>
  )
}
