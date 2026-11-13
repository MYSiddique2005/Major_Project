import { Card } from '../components/common/Card'
import { DetailList } from '../components/common/DetailList'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { useAuth } from '../context/AuthContext'
import { useApi } from '../hooks/useApi'
import { systemService } from '../services/systemService'
import type { SystemInfo } from '../types/system'
import { formatDate, formatRole } from '../utils/format'

const PROVIDERS: Record<SystemInfo['ai_provider'], string> = { gemini: 'Google Gemini', anthropic: 'Anthropic Claude' }

const VERIFIERS: Record<SystemInfo['verifier'], string> = {
  patterns: 'Claim patterns: figures, risk levels and rules checked against the data',
  'trace-rule': 'TRACE, rules only: typed assertions checked by the system\'s own code',
  trace: 'TRACE: typed assertions extracted by the model and checked by the system\'s own code',
  off: 'Off (for experiments only)',
}

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
        <Card title="About this build" subtitle="The settings the server is running with.">
          <QueryBoundary state={system} resource="system information">
            {(info) => (
              <>
                <DetailList
                  items={[
                    { label: 'Version', value: `IntelliERP ${info.version} (all ${info.phase} phases complete)` },
                    {
                      label: 'Data',
                      value: info.persistent
                        ? 'PostgreSQL: data is saved and survives restarts'
                        : 'In-memory demo data: changes are lost when the server restarts',
                    },
                    { label: 'Data as of', value: formatDate(info.business_date) },
                    {
                      label: 'AI assistant',
                      value: info.ai_configured
                        ? `Connected: ${info.ai_model} (${PROVIDERS[info.ai_provider]})`
                        : `Not connected: set the ${info.ai_provider === 'gemini' ? 'GEMINI_API_KEY' : 'ANTHROPIC_API_KEY'} in Backend/.env`,
                    },
                    {
                      label: 'Grounding',
                      value: info.grounding ? 'On: answers use the knowledge base of company rules' : 'Off (for experiments only)',
                    },
                    { label: 'Statement check', value: VERIFIERS[info.verifier] },
                  ]}
                />
                <p className="mt-4 text-xs text-slate-500">
                  Accounts and roles are defined in the seed data; this page shows them but does not edit them. The
                  statement check is set with <code>LLM_VERIFIER</code> in <code>Backend/.env</code>.
                </p>
              </>
            )}
          </QueryBoundary>
        </Card>
      </div>
    </>
  )
}
