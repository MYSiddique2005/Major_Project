import type { LucideIcon } from 'lucide-react'

type Tone = 'default' | 'warning' | 'danger'

const ICON_TONES: Record<Tone, string> = {
  default: 'bg-brand-50 text-brand-700',
  warning: 'bg-amber-50 text-amber-700',
  danger: 'bg-red-50 text-red-700',
}

interface StatCardProps {
  label: string
  value: string
  icon: LucideIcon
  hint?: string
  tone?: Tone
}

export function StatCard({ label, value, icon: Icon, hint, tone = 'default' }: StatCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-500">{label}</p>
        <span className={`rounded-md p-1.5 ${ICON_TONES[tone]}`}>
          <Icon className="size-4" aria-hidden />
        </span>
      </div>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  )
}
