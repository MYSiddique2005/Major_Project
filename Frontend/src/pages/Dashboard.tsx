import {
  AlertOctagon,
  AlertTriangle,
  Boxes,
  ClipboardList,
  DollarSign,
  PackageX,
  ShoppingCart,
  Truck,
} from 'lucide-react'

import { Card } from '../components/common/Card'
import { PageHeader } from '../components/common/PageHeader'
import { QueryBoundary } from '../components/common/QueryBoundary'
import { StatCard } from '../components/common/StatCard'
import { RiskAlertsPanel } from '../components/dashboard/RiskAlertsPanel'
import { SalesTrendChart } from '../components/dashboard/SalesTrendChart'
import { StatusBarChart } from '../components/dashboard/StatusBarChart'
import { useAuth } from '../context/AuthContext'
import { useApi } from '../hooks/useApi'
import { analyticsService } from '../services/analyticsService'
import { dashboardService } from '../services/dashboardService'
import { chartTheme } from '../utils/chartTheme'
import { formatCurrency, formatNumber } from '../utils/format'

function greeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}

function RiskAlerts() {
  const alerts = useApi(analyticsService.getAlerts, [])
  return (
    <Card
      title="Risk Alerts"
      subtitle="High and critical risks found by rule-based analytics over sales, inventory and procurement data. Not AI generated; LLM explanations arrive in a later phase."
      className="lg:col-span-2"
    >
      <QueryBoundary state={alerts} resource="risk alerts">
        {(data) => <RiskAlertsPanel alerts={data} />}
      </QueryBoundary>
    </Card>
  )
}

export default function Dashboard() {
  const { user, hasPermission } = useAuth()
  const summary = useApi(dashboardService.getSummary, [])
  const salesTrend = useApi(dashboardService.getSalesTrend, [])
  const inventoryStatus = useApi(dashboardService.getInventoryStatus, [])
  const procurementStatus = useApi(dashboardService.getProcurementStatus, [])

  return (
    <>
      <PageHeader title={`${greeting()}, ${user?.full_name.split(' ')[0] ?? ''}`} subtitle="Overview of sales, inventory and procurement." />

      <QueryBoundary state={summary} resource="dashboard summary">
        {(data) => (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Total Sales" value={formatCurrency(data.total_sales)} icon={DollarSign} hint="Excludes cancelled orders" />
            <StatCard label="Total Orders" value={formatNumber(data.total_orders)} icon={ShoppingCart} />
            <StatCard label="Inventory Items" value={formatNumber(data.inventory_items)} icon={Boxes} />
            <StatCard label="Active Suppliers" value={formatNumber(data.active_suppliers)} icon={Truck} />
            <StatCard label="Low Stock Items" value={formatNumber(data.low_stock_items)} icon={AlertTriangle} tone="warning" />
            <StatCard label="Critical Stock Items" value={formatNumber(data.critical_stock_items)} icon={AlertOctagon} tone="danger" />
            <StatCard label="Out of Stock" value={formatNumber(data.out_of_stock_items)} icon={PackageX} tone="danger" />
            <StatCard label="Pending Purchase Orders" value={formatNumber(data.pending_purchase_orders)} icon={ClipboardList} hint="Awaiting approval" />
          </div>
        )}
      </QueryBoundary>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Sales Trend" subtitle="Monthly revenue, last 12 months" className="lg:col-span-2">
          <QueryBoundary state={salesTrend} resource="sales trend">
            {(data) => <SalesTrendChart data={data} />}
          </QueryBoundary>
        </Card>

        <Card title="Inventory Status" subtitle="Inventory records by stock status">
          <QueryBoundary state={inventoryStatus} resource="inventory status">
            {(data) => (
              <StatusBarChart
                data={data}
                unit="Records"
                ariaLabel="Inventory records by stock status"
                colors={chartTheme.stockStatus}
              />
            )}
          </QueryBoundary>
        </Card>

        <Card title="Procurement Status" subtitle="Purchase orders by status">
          <QueryBoundary state={procurementStatus} resource="procurement status">
            {(data) => <StatusBarChart data={data} unit="Orders" ariaLabel="Purchase orders by status" />}
          </QueryBoundary>
        </Card>

        {hasPermission('analytics:view') && <RiskAlerts />}
      </div>
    </>
  )
}
