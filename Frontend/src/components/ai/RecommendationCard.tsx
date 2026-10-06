import { AlertTriangle, CheckCircle2, FilePlus2 } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import type { Recommendation } from '../../types'
import { RiskBadge } from '../analytics/RiskBadge'
import { Button } from '../common/Button'

const ACTION_LABELS: Record<Recommendation['action'], string> = {
  reorder: 'Reorder',
  expedite_delivery: 'Expedite delivery',
  review_supplier: 'Review supplier',
  monitor: 'Monitor',
}

const MODULE_LABELS: Record<string, string> = {
  sales: 'Sales',
  inventory: 'Inventory',
  procurement: 'Procurement',
  supplier: 'Supplier',
  rule: 'Company rule',
}

/** What the recommended action is, in one line. */
function actionText(recommendation: Recommendation): string {
  const { action, quantity, product_name, supplier_name } = recommendation
  if (action === 'reorder') {
    return `Order ${quantity?.toLocaleString() ?? '?'} units of ${product_name ?? 'the product'}${supplier_name ? ` from ${supplier_name}` : ''}`
  }
  if (action === 'expedite_delivery') return `Chase the open order${supplier_name ? ` with ${supplier_name}` : ''}`
  if (action === 'review_supplier') return `Review ${supplier_name ?? 'the supplier'}'s delivery record`
  return 'No action needed yet; keep watching'
}

/** The server's checks on the model's text, as short statements. Problems come first. */
function checkResults(recommendation: Recommendation): { ok: boolean; text: string }[] {
  const { checks, quantity, system_quantity, supplier_name, product_name } = recommendation
  const results: { ok: boolean; text: string }[] = []
  if (checks.quantity_matches_rule === true) results.push({ ok: true, text: 'Quantity matches the reorder rule' })
  if (checks.quantity_matches_rule === false) {
    results.push({
      ok: false,
      text: `The reorder rule gives ${system_quantity?.toLocaleString()} units, not ${quantity?.toLocaleString()}`,
    })
  }
  if (checks.supplier_supplies_product === false) {
    results.push({ ok: false, text: `${supplier_name} does not supply ${product_name}` })
  }
  if (checks.figures_unmatched.length > 0) {
    results.push({ ok: false, text: `Figures not found in the system data: ${checks.figures_unmatched.join(', ')}` })
  } else if (checks.figures_checked > 0) {
    results.push({ ok: true, text: `All ${checks.figures_checked} figures match the system data` })
  }
  results.push(
    checks.cross_module
      ? { ok: true, text: 'Evidence from more than one module' }
      : { ok: false, text: 'Evidence from a single module only' },
  )
  return results.sort((a, b) => Number(a.ok) - Number(b.ok))
}

interface RecommendationCardProps {
  recommendation: Recommendation
  /** Shown in the header after the subject, e.g. a status badge. */
  meta?: ReactNode
  /** Buttons shown at the bottom. */
  actions?: ReactNode
  /** Lets the user turn a reorder recommendation into a draft purchase order. Omit to hide the control. */
  draft?: {
    onDraft: () => void
    busy: boolean
    /** The draft already created from this recommendation, if any. */
    purchaseOrderId: string | null
  }
}

/** One AI recommendation: the finding, the action, the evidence by module and the server's checks. */
export function RecommendationCard({ recommendation, meta, actions, draft }: RecommendationCardProps) {
  const canDraft = draft && recommendation.action === 'reorder' && recommendation.checks.supplier_supplies_product !== false
  const subjectLink =
    recommendation.subject_type === 'product'
      ? `/analytics/products/${recommendation.subject_id}`
      : `/suppliers/${recommendation.subject_id}`
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-800">
      <div className="flex flex-wrap items-center gap-2">
        <RiskBadge level={recommendation.severity} />
        <Link to={subjectLink} className="font-medium text-slate-700 hover:underline">
          {recommendation.subject_name} ({recommendation.subject_id})
        </Link>
        {meta}
      </div>
      <h3 className="mt-2 font-semibold text-slate-900">{recommendation.headline}</h3>
      <p className="mt-1 whitespace-pre-wrap text-slate-700">{recommendation.explanation}</p>

      <p className="mt-3 rounded-md bg-slate-50 px-3 py-2">
        <span className="font-semibold">{ACTION_LABELS[recommendation.action]}:</span> {actionText(recommendation)}
      </p>

      <ul className="mt-3 space-y-1">
        {recommendation.evidence.map((item, index) => (
          <li key={index} className="flex gap-2">
            <span className="w-24 shrink-0 text-xs font-medium uppercase tracking-wide text-slate-500">
              {MODULE_LABELS[item.module] ?? item.module}
            </span>
            <span>{item.statement}</span>
          </li>
        ))}
      </ul>

      <ul className="mt-3 space-y-1 border-t border-slate-100 pt-3 text-xs">
        {checkResults(recommendation).map((result) => (
          <li key={result.text} className={`flex items-center gap-1.5 ${result.ok ? 'text-slate-500' : 'text-amber-800'}`}>
            {result.ok ? (
              <CheckCircle2 className="size-3.5 text-emerald-600" aria-hidden />
            ) : (
              <AlertTriangle className="size-3.5" aria-hidden />
            )}
            {result.text}
          </li>
        ))}
      </ul>

      {(actions || canDraft) && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {canDraft &&
            (draft.purchaseOrderId ? (
              <Link to={`/procurement/${draft.purchaseOrderId}`} className="text-sm font-medium text-brand-700 hover:underline">
                Draft {draft.purchaseOrderId} created: review and submit it
              </Link>
            ) : (
              <Button variant="primary" disabled={draft.busy} onClick={draft.onDraft}>
                <FilePlus2 className="size-4" aria-hidden />
                {draft.busy ? 'Creating draft…' : 'Create draft purchase order'}
              </Button>
            ))}
          {actions}
        </div>
      )}
    </article>
  )
}
