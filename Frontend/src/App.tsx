import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/layout/AppLayout'
import { RequireAuth, RequirePermission } from './components/layout/ProtectedRoute'
import AIAssistant from './pages/AIAssistant'
import Analytics from './pages/Analytics'
import AnalyticsProduct from './pages/AnalyticsProduct'
import Approvals from './pages/Approvals'
import AuditLogs from './pages/AuditLogs'
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import InventoryDetail from './pages/InventoryDetail'
import Login from './pages/Login'
import NotFound from './pages/NotFound'
import Procurement from './pages/Procurement'
import ProcurementDetail from './pages/ProcurementDetail'
import ProductDetail from './pages/ProductDetail'
import Products from './pages/Products'
import SaleDetail from './pages/SaleDetail'
import Sales from './pages/Sales'
import Settings from './pages/Settings'
import SupplierDetail from './pages/SupplierDetail'
import Suppliers from './pages/Suppliers'
import type { Permission } from './types'

const guard = (permission: Permission, page: ReactNode) => (
  <RequirePermission permission={permission}>{page}</RequirePermission>
)

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={guard('dashboard:view', <Dashboard />)} />
        <Route path="/sales" element={guard('sales:view', <Sales />)} />
        <Route path="/sales/:id" element={guard('sales:view', <SaleDetail />)} />
        <Route path="/inventory" element={guard('inventory:view', <Inventory />)} />
        <Route path="/inventory/:id" element={guard('inventory:view', <InventoryDetail />)} />
        <Route path="/procurement" element={guard('procurement:view', <Procurement />)} />
        <Route path="/procurement/:id" element={guard('procurement:view', <ProcurementDetail />)} />
        <Route path="/suppliers" element={guard('suppliers:view', <Suppliers />)} />
        <Route path="/suppliers/:id" element={guard('suppliers:view', <SupplierDetail />)} />
        <Route path="/products" element={guard('products:view', <Products />)} />
        <Route path="/products/:id" element={guard('products:view', <ProductDetail />)} />
        <Route path="/analytics" element={guard('analytics:view', <Analytics />)} />
        <Route path="/analytics/products/:id" element={guard('analytics:view', <AnalyticsProduct />)} />
        <Route path="/approvals" element={guard('procurement:approve', <Approvals />)} />
        <Route path="/audit-logs" element={guard('audit:view', <AuditLogs />)} />
        <Route path="/ai-assistant" element={guard('ai:use', <AIAssistant />)} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<Navigate to="/settings" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
