import type { AuditLog } from '../types'
import { api, cleanParams } from './api'

export interface AuditFilters {
  search?: string
  action?: string
  status?: string
  [key: string]: string | undefined
}

export const auditService = {
  getAuditLogs: (filters: AuditFilters = {}) =>
    api.get<AuditLog[]>('/audit-logs', { params: cleanParams(filters) }).then((r) => r.data),
}
