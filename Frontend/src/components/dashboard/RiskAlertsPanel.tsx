import { AlertTriangle, PackageX } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { RiskAlert } from '../../types'
import { RiskBadge } from '../analytics/RiskBadge'
import { EmptyState } from '../common/EmptyState'

/** High and critical findings from the rule-based analytics engine (not AI). */
export function RiskAlertsPanel({ alerts }: { alerts: RiskAlert[] }) {
  if (alerts.length === 0) return <EmptyState message="No high or critical risks right now." />
  return (
    <ul className="divide-y divide-slate-100">
      {alerts.map((alert) => {
        const Icon = alert.category === 'Stockout Risk' ? PackageX : AlertTriangle
        const to = alert.entity === 'product' ? `/analytics/products/${alert.entity_id}` : `/suppliers/${alert.entity_id}`
        return (
          <li key={alert.id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
            <span className={`mt-0.5 rounded-md p-1.5 ${alert.severity === 'Critical' ? 'bg-red-50 text-red-700' : 'bg-orange-50 text-orange-700'}`}>
              <Icon className="size-4" aria-hidden />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-medium text-slate-500">{alert.category}</span>
                <RiskBadge level={alert.severity} />
              </div>
              <Link to={to} className="mt-1 block text-sm font-medium text-slate-900 hover:underline">
                {alert.title}
              </Link>
              <p className="mt-0.5 text-sm text-slate-600">{alert.message}</p>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
