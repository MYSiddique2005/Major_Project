import { AlertTriangle, CheckCircle2, Sparkles } from 'lucide-react'

import type { PurchaseOrder } from '../../types'

const MODULE_LABELS: Record<string, string> = {
  sales: 'Sales',
  inventory: 'Inventory',
  procurement: 'Procurement',
  supplier: 'Supplier',
  rule: 'Company rule',
}

/**
 * For a purchase order drafted from an AI recommendation: what the AI said and what the server's
 * checks found, so whoever reviews or approves the order can judge it. `compact` shows the
 * headline and any warnings only.
 */
export function AiOriginNotice({ order, compact = false }: { order: PurchaseOrder; compact?: boolean }) {
  const kept = order.ai_recommendation
  if (order.origin === 'Manual' || !kept) return null
  const { checks } = kept
  const warnings: string[] = []
  if (checks.quantity_matches_rule === false) {
    warnings.push(
      `The reorder rule gave ${kept.system_quantity?.toLocaleString()} units when this was drafted; the AI proposed a different quantity.`,
    )
  }
  if (checks.figures_unmatched.length > 0) {
    warnings.push(`Figures in the AI's text not found in the system data: ${checks.figures_unmatched.join(', ')}.`)
  }
  for (const claim of checks.claims_contradicted ?? []) {
    warnings.push(`A statement in the AI's reasoning contradicts the system data: ${claim}.`)
  }
  if (!checks.cross_module) warnings.push("The AI's evidence came from a single module.")

  return (
    <div className="rounded-lg border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-950">
      <p className="flex items-center gap-2 font-semibold">
        <Sparkles className="size-4" aria-hidden />
        Drafted from an {order.origin === 'AI Insight' ? `AI insight (${order.origin_ref})` : 'AI assistant recommendation'}
        {kept.requested_by && <span className="font-normal">for {kept.requested_by}</span>}
      </p>
      <p className="mt-1">{kept.headline}</p>
      {!compact && <p className="mt-1 whitespace-pre-wrap text-violet-900">{kept.explanation}</p>}
      {!compact && (
        <ul className="mt-2 space-y-1">
          {kept.evidence.map((item, index) => (
            <li key={index} className="flex gap-2">
              <span className="w-24 shrink-0 text-xs font-medium uppercase tracking-wide text-violet-700">
                {MODULE_LABELS[item.module] ?? item.module}
              </span>
              <span>{item.statement}</span>
            </li>
          ))}
        </ul>
      )}
      {warnings.length > 0 ? (
        <ul className="mt-2 space-y-1 text-amber-900">
          {warnings.map((warning) => (
            <li key={warning} className="flex items-start gap-1.5">
              <AlertTriangle className="mt-0.5 size-3.5 shrink-0" aria-hidden />
              {warning}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 flex items-center gap-1.5 text-xs text-violet-800">
          <CheckCircle2 className="size-3.5 text-emerald-600" aria-hidden />
          Quantity, supplier and figures matched the system's own data when this was drafted.
        </p>
      )}
      <p className="mt-2 text-xs text-violet-800">
        The AI only prepared this draft. It has the same validation, review and approval as any other purchase order.
      </p>
    </div>
  )
}
