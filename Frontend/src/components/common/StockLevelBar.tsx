import type { StockStatus } from '../../types'

const BAR_CLASSES: Record<StockStatus, string> = {
  'In Stock': 'bg-emerald-500',
  'Low Stock': 'bg-amber-500',
  Critical: 'bg-orange-500',
  'Out of Stock': 'bg-red-500',
}

interface StockLevelBarProps {
  current: number
  reorderLevel: number
  status: StockStatus
}

/** Stock on hand relative to twice the reorder level (so the reorder point sits mid-bar). */
export function StockLevelBar({ current, reorderLevel, status }: StockLevelBarProps) {
  const scale = Math.max(reorderLevel * 2, 1)
  const percent = Math.min(100, Math.round((current / scale) * 100))
  return (
    <div
      className="relative h-1.5 w-24 rounded-full bg-slate-200"
      role="img"
      aria-label={`${current} in stock, reorder level ${reorderLevel}`}
    >
      <div className={`h-full rounded-full ${BAR_CLASSES[status]}`} style={{ width: `${percent}%` }} />
      <span className="absolute -top-0.5 left-1/2 h-2.5 w-px bg-slate-500" aria-hidden />
    </div>
  )
}
