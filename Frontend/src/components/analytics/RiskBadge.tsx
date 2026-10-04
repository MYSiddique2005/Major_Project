import type { RiskLevel } from '../../types'
import { StatusBadge, type Tone } from '../common/StatusBadge'

const RISK_TONES: Record<RiskLevel, Tone> = { Critical: 'red', High: 'orange', Medium: 'amber', Low: 'green' }

export function RiskBadge({ level }: { level: RiskLevel }) {
  return <StatusBadge status={level} tone={RISK_TONES[level]} />
}
