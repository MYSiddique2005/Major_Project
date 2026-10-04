interface LegendItem {
  label: string
  color: string
  dashed?: boolean
}

/** Line-chart legend. Labels stay in text colour; the swatch carries the series identity. */
export function ChartLegend({ items }: { items: LegendItem[] }) {
  return (
    <ul className="mb-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-600">
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-2">
          <svg width="22" height="6" aria-hidden>
            <line x1="0" y1="3" x2="22" y2="3" stroke={item.color} strokeWidth="2" strokeDasharray={item.dashed ? '5 4' : undefined} />
          </svg>
          {item.label}
        </li>
      ))}
    </ul>
  )
}
