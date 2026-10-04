interface ChartTooltipProps {
  title: string
  rows: { label: string; value: string }[]
}

export function ChartTooltip({ title, rows }: ChartTooltipProps) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs shadow-md">
      <p className="font-medium text-slate-900">{title}</p>
      {rows.map((row) => (
        <p key={row.label} className="mt-0.5 flex justify-between gap-4 text-slate-600">
          <span>{row.label}</span>
          <span className="font-medium text-slate-900 tabular-nums">{row.value}</span>
        </p>
      ))}
    </div>
  )
}
