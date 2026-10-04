import type { SystemInfo } from '../types'
import { api } from './api'

export const systemService = {
  getInfo: () => api.get<SystemInfo>('/system/info').then((r) => r.data),
}
