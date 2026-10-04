import type { TokenResponse, User } from '../types'
import { api } from './api'

export const authService = {
  login: (username: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { username, password }).then((r) => r.data),
  getCurrentUser: () => api.get<User>('/auth/me').then((r) => r.data),
}
