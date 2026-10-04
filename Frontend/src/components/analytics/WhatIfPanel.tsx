import { useEffect, useState, type FormEvent } from 'react'

import { getErrorMessage } from '../../services/api'
import { analyticsService } from '../../services/analyticsService'
import type { WhatIfOutcome, WhatIfResult } from '../../types'
import { formatDate, formatNumber } from '../../utils/format'
import { Button } from '../common/Button'
import { ErrorState } from '../common/ErrorState'
import { LoadingSpinner } from '../common/LoadingSpinner'
import { WhatIfChart } from './WhatIfChart'

const HORIZONS = [30, 60, 90, 120]

function comparisonRows(baseline: WhatIfOutcome, scenario: WhatIfOutcome) {
  const stockout = (o: WhatIfOutcome) =>
    o.stockout_date ? `${formatDate(o.stockout_date)} (day ${o.days_until_stockout})` : 'None in this period'
  return [
    { label: 'Daily demand', values: [baseline, scenario].map((o) => `${o.daily_demand} units`) },
    { label: 'Supplier lead time', values: [baseline, scenario].map((o) => `${o.lead_time_days} days`) },
    { label: 'First stockout', values: [baseline, scenario].map(stockout) },
    { label: 'Days below safety stock', values: [baseline, scenario].map((o) => String(o.days_below_safety)) },
    { label: 'Demand not served', values: [baseline, scenario].map((o) => `${formatNumber(Math.round(o.unmet_demand_units))} units`) },
    { label: 'Stock at end of period', values: [baseline, scenario].map((o) => formatNumber(Math.round(o.ending_stock))) },
  ]
}

/** Scenario inputs, projected-stock chart and baseline/scenario comparison. Read-only: nothing is saved. */
export function WhatIfPanel({ productId }: { productId: string }) {
  const [demandChange, setDemandChange] = useState('0')
  const [leadTimeChange, setLeadTimeChange] = useState('0')
  const [orderQuantity, setOrderQuantity] = useState('0')
  const [horizon, setHorizon] = useState('60')
  const [result, setResult] = useState<WhatIfResult | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    setRunning(true)
    setError(null)
    try {
      setResult(
        await analyticsService.runWhatIf({
          product_id: productId,
          demand_change_pct: Number(demandChange) || 0,
          lead_time_change_days: Math.round(Number(leadTimeChange)) || 0,
          order_quantity: Math.round(Number(orderQuantity)) || 0,
          horizon_days: Number(horizon),
        }),
      )
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setRunning(false)
    }
  }

  // Show the unchanged projection as soon as the panel opens.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => void run(), [productId])

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    void run()
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="grid grid-cols-2 items-end gap-4 lg:grid-cols-5">
        <div>
          <label htmlFor="whatif-demand" className="field-label">
            Demand change (%)
          </label>
          <input id="whatif-demand" type="number" min={-100} max={500} className="field" value={demandChange} onChange={(e) => setDemandChange(e.target.value)} />
        </div>
        <div>
          <label htmlFor="whatif-lead" className="field-label">
            Delivery delay (days)
          </label>
          <input id="whatif-lead" type="number" min={-30} max={90} step={1} className="field" value={leadTimeChange} onChange={(e) => setLeadTimeChange(e.target.value)} />
        </div>
        <div>
          <label htmlFor="whatif-order" className="field-label">
            Order today (units)
          </label>
          <input id="whatif-order" type="number" min={0} step={1} className="field" value={orderQuantity} onChange={(e) => setOrderQuantity(e.target.value)} />
        </div>
        <div>
          <label htmlFor="whatif-horizon" className="field-label">
            Period
          </label>
          <select id="whatif-horizon" className="field" value={horizon} onChange={(e) => setHorizon(e.target.value)}>
            {HORIZONS.map((days) => (
              <option key={days} value={days}>
                {days} days
              </option>
            ))}
          </select>
        </div>
        <Button type="submit" variant="primary" disabled={running}>
          {running ? 'Running...' : 'Run scenario'}
        </Button>
      </form>

      <div className="mt-6">
        {error ? (
          <ErrorState message={`Unable to run the scenario. ${error}`} onRetry={run} />
        ) : !result ? (
          <LoadingSpinner label="Projecting stock..." />
        ) : (
          <div className={running ? 'opacity-60' : undefined}>
            <WhatIfChart result={result} />
            <div className="mt-5 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <caption className="sr-only">Baseline compared with scenario</caption>
                <thead className="border-b border-slate-200 text-xs font-medium tracking-wide text-slate-500 uppercase">
                  <tr>
                    <th scope="col" className="py-2 pr-4">Measure</th>
                    <th scope="col" className="px-4 py-2">Baseline</th>
                    <th scope="col" className="px-4 py-2">Scenario</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {comparisonRows(result.baseline, result.scenario).map((row) => (
                    <tr key={row.label}>
                      <th scope="row" className="py-2 pr-4 font-normal text-slate-600">{row.label}</th>
                      <td className="px-4 py-2 text-slate-900">{row.values[0]}</td>
                      <td className={`px-4 py-2 ${row.values[0] === row.values[1] ? 'text-slate-900' : 'font-semibold text-slate-900'}`}>
                        {row.values[1]}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <ul className="mt-4 list-disc space-y-1 pl-5 text-xs text-slate-500">
              {result.assumptions.map((assumption) => (
                <li key={assumption}>{assumption}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
