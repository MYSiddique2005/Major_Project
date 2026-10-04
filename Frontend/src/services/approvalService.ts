import type { Approval } from '../types'
import { api, cleanParams } from './api'

const path = (id: string) => `/approvals/${encodeURIComponent(id)}`

export const approvalService = {
  getApprovals: (status?: string) =>
    api.get<Approval[]>('/approvals', { params: cleanParams({ status }) }).then((r) => r.data),
  getApproval: (id: string) => api.get<Approval>(path(id)).then((r) => r.data),
  approve: (id: string, comment?: string) =>
    api.post<Approval>(`${path(id)}/approve`, { comment: comment || null }).then((r) => r.data),
  reject: (id: string, comment?: string) =>
    api.post<Approval>(`${path(id)}/reject`, { comment: comment || null }).then((r) => r.data),
}
