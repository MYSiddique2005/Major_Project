export type Tone = 'green' | 'amber' | 'orange' | 'red' | 'blue' | 'slate'

const TONE_CLASSES: Record<Tone, string> = {
  green: 'bg-emerald-50 text-emerald-800 ring-emerald-600/20',
  amber: 'bg-amber-50 text-amber-800 ring-amber-600/25',
  orange: 'bg-orange-50 text-orange-800 ring-orange-600/25',
  red: 'bg-red-50 text-red-800 ring-red-600/20',
  blue: 'bg-blue-50 text-blue-800 ring-blue-600/20',
  slate: 'bg-slate-100 text-slate-700 ring-slate-500/20',
}

const DOT_CLASSES: Record<Tone, string> = {
  green: 'bg-emerald-500',
  amber: 'bg-amber-500',
  orange: 'bg-orange-500',
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  slate: 'bg-slate-400',
}

const STATUS_TONES: Record<string, Tone> = {
  // Sales
  Pending: 'amber',
  Processing: 'blue',
  Completed: 'green',
  Cancelled: 'slate',
  // Stock
  'In Stock': 'green',
  'Low Stock': 'amber',
  Critical: 'orange',
  'Out of Stock': 'red',
  // Procurement / approvals
  Draft: 'slate',
  'Pending Approval': 'amber',
  Approved: 'green',
  Rejected: 'red',
  Ordered: 'blue',
  Delivered: 'green',
  // Suppliers / products
  Active: 'green',
  Inactive: 'slate',
  Discontinued: 'slate',
  // Audit
  SUCCESS: 'green',
  FAILED: 'red',
}

/** `tone` overrides the default colour for the status text. */
export function StatusBadge({ status, tone: toneOverride }: { status: string; tone?: Tone }) {
  const tone = toneOverride ?? STATUS_TONES[status] ?? 'slate'
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap ring-1 ring-inset ${TONE_CLASSES[tone]}`}
    >
      <span className={`size-1.5 rounded-full ${DOT_CLASSES[tone]}`} aria-hidden />
      {status}
    </span>
  )
}
