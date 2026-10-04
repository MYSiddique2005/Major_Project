export type Role = 'ADMIN' | 'INVENTORY_MANAGER' | 'PROCUREMENT_MANAGER' | 'EMPLOYEE'

/** Permission strings issued by the backend (app/security/permissions.py). */
export type Permission =
  | 'dashboard:view'
  | 'sales:view'
  | 'inventory:view'
  | 'products:view'
  | 'suppliers:view'
  | 'procurement:view'
  | 'procurement:create'
  | 'procurement:approve'
  | 'analytics:view'
  | 'audit:view'
  | 'users:manage'
  | 'ai:use'

export interface User {
  id: string
  username: string
  full_name: string
  email: string
  role: Role
  permissions: Permission[]
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}
