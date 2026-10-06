import { Info, RefreshCw } from 'lucide-react'
import { useState } from 'react'

import { RecommendationCard } from '../components/ai/RecommendationCard'
import { Button } from '../components/common/Button'
import { EmptyState } from '../components/common/EmptyState'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatusBadge } from '../components/common/StatusBadge'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'
import { getErrorMessage } from '../services/api'
import { insightService } from '../services/insightService'
import type { AiInsight, AiScan } from '../types'
import { formatDateTime } from '../utils/format'

/** "Scheduled scan, 6 Oct 2026 09:00: 6 insights from 17 findings (gemini-3.8-flash)". */
function scanSummary(scan: AiScan): string {
  const who = scan.trigger === 'schedule' ? 'Scheduled scan' : `Scan by ${scan.trigger}`
  const when = formatDateTime(scan.started_at)
  if (scan.status === 'Running') return `${who}, ${when}: running`
  if (scan.status === 'Failed') return `${who}, ${when}: failed. ${scan.message}`
  const model = scan.model ? ` (${scan.model})` : ''
  return `${who}, ${when}: ${scan.insights} insights from ${scan.findings} findings${model}. ${scan.message}`
}

export default function AIInsights() {
  const { hasPermission } = useAuth()
  const toast = useToast()
  const [showPast, setShowPast] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [busyId, setBusyId] = useState<string | null>(null)
  const insights = useApi(() => insightService.list({ includePast: showPast }), [showPast])
  const scans = useApi(() => insightService.listScans(1), [])
  const canAct = hasPermission('ai:use')

  const runScan = async () => {
    setScanning(true)
    try {
      const scan = await insightService.runScan()
      if (scan.status === 'Failed') toast.error(`Scan failed. ${scan.message}`)
      else toast.success(`Scan finished: ${scan.insights} insights from ${scan.findings} findings.`)
    } catch (err) {
      toast.error(getErrorMessage(err, 'The scan could not be run.'))
    } finally {
      setScanning(false)
      insights.reload()
      scans.reload()
    }
  }

  const review = async (insight: AiInsight, decision: 'acknowledge' | 'dismiss') => {
    setBusyId(insight.id)
    try {
      await insightService[decision](insight.id)
      insights.reload()
    } catch (err) {
      toast.error(getErrorMessage(err, 'The insight could not be updated.'))
    } finally {
      setBusyId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="AI Insights"
        subtitle="Risks the assistant found and explained without being asked."
        actions={
          canAct && (
            <Button variant="primary" onClick={() => void runScan()} disabled={scanning}>
              <RefreshCw className={`size-4 ${scanning ? 'animate-spin' : ''}`} aria-hidden />
              {scanning ? 'Scanning…' : 'Run scan now'}
            </Button>
          )
        }
      />

      <div className="mb-4 flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
        <Info className="mt-0.5 size-4 shrink-0" aria-hidden />
        <p>
          The rule-based analytics decide what is at risk and how severe it is. The AI model writes the explanation and
          the recommended action from the sales, inventory and procurement facts, and each one is then checked against
          the system's own figures. An insight creates no order.
          {scans.data?.[0] && <span className="mt-1 block text-blue-800">Last scan: {scanSummary(scans.data[0])}</span>}
        </p>
      </div>

      <label className="mb-3 flex items-center gap-2 text-sm text-slate-600">
        <input type="checkbox" checked={showPast} onChange={(event) => setShowPast(event.target.checked)} />
        Show dismissed and superseded insights
      </label>

      <QueryBoundary state={insights} resource="AI insights">
        {(data) =>
          data.length === 0 ? (
            <EmptyState message="No insights yet. Run a scan to analyse the current high and critical risks." />
          ) : (
            <div className="space-y-3">
              {data.map((insight) => (
                <RecommendationCard
                  key={insight.id}
                  recommendation={insight}
                  meta={
                    <>
                      <StatusBadge status={insight.status} tone={insight.status === 'New' ? 'blue' : 'slate'} />
                      <span className="text-xs text-slate-500">{formatDateTime(insight.created_at)}</span>
                    </>
                  }
                  actions={
                    canAct &&
                    (insight.status === 'New' || insight.status === 'Acknowledged') && (
                      <>
                        {insight.status === 'New' && (
                          <Button disabled={busyId === insight.id} onClick={() => void review(insight, 'acknowledge')}>
                            Acknowledge
                          </Button>
                        )}
                        <Button variant="ghost" disabled={busyId === insight.id} onClick={() => void review(insight, 'dismiss')}>
                          Dismiss
                        </Button>
                      </>
                    )
                  }
                />
              ))}
            </div>
          )
        }
      </QueryBoundary>
    </>
  )
}
