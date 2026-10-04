import { useState } from 'react'

import { Card } from '../components/common/Card'
import { DataTable, type Column } from '../components/common/DataTable'
import { FilterDropdown } from '../components/common/FilterDropdown'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { SearchBar } from '../components/common/SearchBar'
import { StatusBadge } from '../components/common/StatusBadge'
import { Toolbar } from '../components/common/Toolbar'
import { useApi } from '../hooks/useApi'
import { useDebounce } from '../hooks/useDebounce'
import { auditService } from '../services/auditService'
import { AUDIT_ACTIONS, AUDIT_STATUSES, type AuditLog } from '../types'
import { formatDateTime } from '../utils/format'

const COLUMNS: Column<AuditLog>[] = [
  { header: 'Timestamp', render: (log) => formatDateTime(log.timestamp), className: 'whitespace-nowrap' },
  { header: 'User', render: (log) => log.username },
  { header: 'Action', render: (log) => <code className="text-xs text-slate-800">{log.action}</code> },
  { header: 'Entity', render: (log) => log.entity },
  { header: 'Entity ID', render: (log) => log.entity_id, className: 'whitespace-nowrap' },
  { header: 'Status', render: (log) => <StatusBadge status={log.status} /> },
  { header: 'Description', render: (log) => log.description },
]

export default function AuditLogs() {
  const [search, setSearch] = useState('')
  const [action, setAction] = useState('')
  const [status, setStatus] = useState('')
  const debouncedSearch = useDebounce(search)
  const logs = useApi(
    () => auditService.getAuditLogs({ search: debouncedSearch, action, status }),
    [debouncedSearch, action, status],
  )

  return (
    <>
      <PageHeader title="Audit Logs" subtitle="Record of logins and purchase-order actions, newest first." />
      <Card padded={false}>
        <Toolbar>
          <SearchBar value={search} onChange={setSearch} placeholder="Search users, entities, descriptions" />
          <FilterDropdown label="Actions" value={action} options={AUDIT_ACTIONS} onChange={setAction} />
          <FilterDropdown label="Statuses" value={status} options={AUDIT_STATUSES} onChange={setStatus} />
        </Toolbar>
        <QueryBoundary state={logs} resource="audit logs">
          {(rows) => (
            <DataTable
              caption="Audit logs"
              columns={COLUMNS}
              rows={rows}
              rowKey={(log) => log.id}
              pageSize={15}
              emptyMessage="No audit events found."
            />
          )}
        </QueryBoundary>
      </Card>
    </>
  )
}
