import {
  Boxes,
  ClipboardCheck,
  ClipboardList,
  LayoutDashboard,
  LineChart,
  Package,
  ScrollText,
  Settings,
  ShoppingCart,
  Sparkles,
  Truck,
  type LucideIcon,
} from 'lucide-react'

import type { Permission } from '../../types'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
  /** Hidden from users without this permission. Omit for pages every user can open. */
  permission?: Permission
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, permission: 'dashboard:view' },
  { to: '/sales', label: 'Sales', icon: ShoppingCart, permission: 'sales:view' },
  { to: '/inventory', label: 'Inventory', icon: Boxes, permission: 'inventory:view' },
  { to: '/procurement', label: 'Procurement', icon: ClipboardList, permission: 'procurement:view' },
  { to: '/suppliers', label: 'Suppliers', icon: Truck, permission: 'suppliers:view' },
  { to: '/products', label: 'Products', icon: Package, permission: 'products:view' },
  { to: '/analytics', label: 'Analytics', icon: LineChart, permission: 'analytics:view' },
  { to: '/approvals', label: 'Approvals', icon: ClipboardCheck, permission: 'procurement:approve' },
  { to: '/ai-assistant', label: 'AI Assistant', icon: Sparkles, permission: 'ai:use' },
  { to: '/audit-logs', label: 'Audit Logs', icon: ScrollText, permission: 'audit:view' },
  { to: '/settings', label: 'Settings', icon: Settings },
]
