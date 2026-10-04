import { Card } from '../components/common/Card'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { useAuth } from '../context/AuthContext'
import { useApi } from '../hooks/useApi'
import { systemService } from '../services/systemService'
import { formatRole } from '../utils/format'

export default function Settings() {
  const { user } = useAuth()
  const system = useApi(systemService.getInfo, [])
  if (!user) return null

  return (
    <>
      <PageHeader title="Settings" subtitle="Your profile and access." />
      <div className="space-y-6">
        <Card title="Profile">
          <DetailList
            items={[
              { label: 'Name', value: user.full_name },
              { label: 'Username', value: user.username },
              { label: 'Email', value: user.email },
              { label: 'Role', value: formatRole(user.role) },
              { label: 'User ID', value: user.id },
            ]}
          />
        </Card>
        <Card title="Permissions" subtitle="Granted by your role and enforced by the server on every request.">
          <ul className="flex flex-wrap gap-2">
            {user.permissions.map((permission) => (
              <li key={permission} className="rounded-md bg-slate-100 px-2 py-1 font-mono text-xs text-slate-700">
                {permission}
              </li>
            ))}
          </ul>
        </Card>
        <Card title="About this build">
          <QueryBoundary state={system} resource="system information">
            {(info) => (
              <p className="text-sm text-slate-600">
                IntelliERP Phase {info.phase}.{' '}
                {info.persistent
                  ? 'ERP data is stored in PostgreSQL and survives restarts.'
                  : 'Running on the in-memory backend: changes are lost when the server restarts.'}{' '}
                No AI model is connected yet. Editing profiles and managing users are planned for a later phase.
              </p>
            )}
          </QueryBoundary>
        </Card>
      </div>
    </>
  )
}
