"""The tools the LLM may call. This list is the whole of what the assistant can do.

Every tool is read-only, wraps a service the rest of the application already uses, and names the
permission it needs. A user is only offered the tools their role allows, and the check is repeated
when a tool runs, so the assistant can never show data the user could not open themselves.
All figures come from these functions; the model does no arithmetic of its own on ERP data.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field, ValidationError

from app.core.exceptions import DomainError
from app.knowledge.base import CATEGORIES, KnowledgeBase
from app.models.entities import User
from app.models.enums import PurchaseOrderStatus, RiskLevel, SalesStatus
from app.schemas.analytics import WhatIfRequest
from app.security.permissions import Permission, has_permission
from app.services.analytics_service import AnalyticsService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.product_service import ProductService
from app.services.sales_service import SalesService
from app.services.supplier_service import SupplierService

MAX_ROWS = 50


# --- Tool inputs ----------------------------------------------------------------------------


class NoInput(BaseModel):
    pass


class StockRiskListInput(BaseModel):
    risk_level: RiskLevel | None = Field(default=None, description="Only products at this risk level")
    search: str | None = Field(default=None, description="Text in the product name, SKU, category or supplier name")
    limit: int = Field(default=15, ge=1, le=MAX_ROWS, description="Most urgent products first")


class ProductInput(BaseModel):
    product_id: str = Field(description="Product ID such as P001")


class ForecastInput(ProductInput):
    horizon_weeks: int = Field(default=8, ge=1, le=26)


class ProductSearchInput(BaseModel):
    search: str | None = Field(default=None, description="Text in the product name, SKU, ID or category")
    category: str | None = Field(default=None, description="Exact category name")
    limit: int = Field(default=20, ge=1, le=MAX_ROWS)


class SalesSummaryInput(BaseModel):
    product_id: str | None = Field(default=None, description="Omit for all products")
    days: int = Field(default=90, ge=1, le=366, description="Look back this many days from today")


class PurchaseOrderListInput(BaseModel):
    product_id: str | None = None
    supplier_id: str | None = Field(default=None, description="Supplier ID such as S004")
    status: PurchaseOrderStatus | None = None
    limit: int = Field(default=20, ge=1, le=MAX_ROWS, description="Newest orders first")


class SupplierSearchInput(BaseModel):
    search: str | None = Field(default=None, description="Text in the supplier name, ID, contact or country")


class KnowledgeSearchInput(BaseModel):
    query: str = Field(min_length=2, description="The term, rule or table to look up, in plain words")
    category: Literal[CATEGORIES] | None = Field(default=None, description="Restrict to one kind of passage")
    limit: int = Field(default=3, ge=1, le=8)


# --- Tools ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    permission: Permission
    input_model: type[BaseModel]
    handler: Callable[[Any], Any]

    def definition(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_model.model_json_schema()}


class ToolError(Exception):
    """Returned to the model as an error result so it can correct itself or tell the user."""


class Toolbox:
    def __init__(
        self,
        analytics: AnalyticsService,
        products: ProductService,
        inventory: InventoryService,
        sales: SalesService,
        suppliers: SupplierService,
        procurement: ProcurementService,
        knowledge: KnowledgeBase | None = None,
    ):
        self._knowledge = knowledge
        self._analytics = analytics
        self._products = products
        self._inventory = inventory
        self._sales = sales
        self._suppliers = suppliers
        self._procurement = procurement
        self._tools = {tool.name: tool for tool in self._build()}

    def available(self, user: User) -> list[Tool]:
        return [tool for tool in self._tools.values() if has_permission(user.role, tool.permission)]

    def run(self, user: User, name: str, arguments: Any) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolError(f"Unknown tool '{name}'.")
        if not has_permission(user.role, tool.permission):
            raise ToolError(f"The user's role does not have the '{tool.permission}' permission.")
        try:
            return tool.handler(tool.input_model.model_validate(arguments))
        except ValidationError as error:
            raise ToolError(f"Invalid input: {error.errors(include_url=False, include_input=False)}") from error
        except DomainError as error:
            raise ToolError(error.message) from error

    def _build(self) -> list[Tool]:
        tools = self._data_tools()
        if self._knowledge is not None:
            tools.append(Tool(
                "search_knowledge",
                "Look up the company's own definitions, business rules, workflows, table and column meanings, "
                "role permissions and data notes. Use it whenever an answer depends on what a term means here, "
                "how a figure or risk level is calculated, or what a rule allows, and the passages already "
                "given do not cover it.",
                Permission.AI_USE, KnowledgeSearchInput, self._search_knowledge,
            ))
        return tools

    def _data_tools(self) -> list[Tool]:
        return [
            Tool(
                "list_stock_risk",
                "Stockout risk for active products, most urgent first, with the counts per risk level. Each row "
                "combines sales (demand and its trend), inventory (stock on hand, safety stock) and procurement "
                "(lead time, units on order, overdue units). Use it to find which products are at risk or need "
                "reordering.",
                Permission.ANALYTICS_VIEW, StockRiskListInput, self._list_stock_risk,
            ),
            Tool(
                "get_stock_risk",
                "Full stockout-risk assessment of one product: risk level, the facts that produced it (drivers), "
                "days of cover, projected stockout date, reorder point, and the suggested order quantity and "
                "supplier. Use it to explain why a product is at risk.",
                Permission.ANALYTICS_VIEW, ProductInput, self._get_stock_risk,
            ),
            Tool(
                "get_demand_forecast",
                "Weekly demand history (26 weeks) and forecast for one product, with the forecasting method "
                "chosen and its backtest error.",
                Permission.ANALYTICS_VIEW, ForecastInput, self._get_forecast,
            ),
            Tool(
                "list_supplier_performance",
                "Delivery performance of every supplier from purchase-order history: on-time rate, average and "
                "longest delay, observed lead time, delay trend, open and overdue orders, and a risk level.",
                Permission.ANALYTICS_VIEW, NoInput, self._list_supplier_performance,
            ),
            Tool(
                "list_risk_alerts",
                "Current high and critical alerts for products (stockout risk) and suppliers (delivery risk).",
                Permission.ANALYTICS_VIEW, NoInput, self._list_alerts,
            ),
            Tool(
                "run_what_if",
                "Project one product's stock day by day under a scenario and compare it with the baseline: "
                "demand_change_pct (30 = demand 30% higher), lead_time_change_days (5 = deliveries 5 days later), "
                "order_quantity (units ordered today). Read-only; nothing is ordered.",
                Permission.ANALYTICS_VIEW, WhatIfRequest, self._run_what_if,
            ),
            Tool(
                "search_products",
                "Find products by name, SKU, ID or category. Returns ID, name, category, supplier, price, unit "
                "cost, current stock and stock status. Use it to turn a product name into its ID.",
                Permission.PRODUCTS_VIEW, ProductSearchInput, self._search_products,
            ),
            Tool(
                "get_inventory",
                "Stock records of one product per warehouse: current stock, safety stock, reorder level and "
                "stock status.",
                Permission.INVENTORY_VIEW, ProductInput, self._get_inventory,
            ),
            Tool(
                "get_sales_summary",
                "Sales over the last N days, cancelled orders excluded: units, revenue, order count, units per "
                "week, and top customers. For one product, or for all products with the top products by revenue.",
                Permission.SALES_VIEW, SalesSummaryInput, self._get_sales_summary,
            ),
            Tool(
                "list_purchase_orders",
                "Purchase orders, newest first, filtered by product, supplier or status, with the count per "
                "status. Shows quantities, order date, expected and actual delivery dates.",
                Permission.PROCUREMENT_VIEW, PurchaseOrderListInput, self._list_purchase_orders,
            ),
            Tool(
                "list_suppliers",
                "Supplier master data: ID, name, contact, country, stated average delivery days, reliability "
                "percentage, status and number of products supplied.",
                Permission.SUPPLIERS_VIEW, SupplierSearchInput, self._list_suppliers,
            ),
        ]

    # --- Handlers ---------------------------------------------------------------------------

    def _search_knowledge(self, args: KnowledgeSearchInput) -> list[dict]:
        matches = self._knowledge.search(args.query, args.limit, args.category)
        if not matches:
            raise ToolError("The knowledge base has nothing on that. Say so rather than assuming a definition.")
        return [{**match.entry.summary(), "text": match.entry.text} for match in matches]

    def _list_stock_risk(self, args: StockRiskListInput) -> dict:
        items = self._analytics.list_stock_risk(args.risk_level, args.search)
        fields = {
            "product_id", "product_name", "category", "risk_level", "on_hand", "safety_stock", "avg_daily_demand",
            "demand_trend_pct", "days_of_cover", "projected_stockout_date", "supplier_id", "supplier_name",
            "lead_time_days", "inbound_units", "overdue_inbound_units", "suggested_order_quantity",
        }
        return {
            "matching_products": len(items),
            "count_by_risk_level": dict(Counter(item.risk_level.value for item in items)),
            "shown": min(len(items), args.limit),
            "products": [item.model_dump(mode="json", include=fields) for item in items[: args.limit]],
        }

    def _get_stock_risk(self, args: ProductInput) -> dict:
        return self._analytics.get_stock_risk(args.product_id).model_dump(mode="json")

    def _get_forecast(self, args: ForecastInput) -> dict:
        return self._analytics.get_forecast(args.product_id, args.horizon_weeks).model_dump(mode="json")

    def _list_supplier_performance(self, _: NoInput) -> list[dict]:
        return [item.model_dump(mode="json") for item in self._analytics.list_supplier_performance()]

    def _list_alerts(self, _: NoInput) -> list[dict]:
        return [alert.model_dump(mode="json", exclude={"id", "source"}) for alert in self._analytics.list_alerts()]

    def _run_what_if(self, args: WhatIfRequest) -> dict:
        # The day-by-day points are for charts; the summary figures are what an answer needs.
        without_points = {"baseline": {"points"}, "scenario": {"points"}}
        return self._analytics.run_what_if(args).model_dump(mode="json", exclude=without_points)

    def _search_products(self, args: ProductSearchInput) -> dict:
        products = self._products.list_products(args.search, args.category)
        return {
            "matching_products": len(products),
            "products": [product.model_dump(mode="json") for product in products[: args.limit]],
        }

    def _get_inventory(self, args: ProductInput) -> list[dict]:
        records = self._inventory.list_inventory(product_id=args.product_id)
        if not records:
            raise ToolError(f"No stock records for product '{args.product_id}'.")
        return [record.model_dump(mode="json", exclude={"sku"}) for record in records]

    def _get_sales_summary(self, args: SalesSummaryInput) -> dict:
        today = date.today()
        since = today - timedelta(days=args.days)
        orders = [
            order for order in self._sales.list_orders(product_id=args.product_id)
            if order.order_date > since and order.status != SalesStatus.CANCELLED
        ]
        weekly: dict[date, int] = defaultdict(int)
        customers: dict[str, float] = defaultdict(float)
        products: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0, 0.0])
        for order in orders:
            weekly[order.order_date - timedelta(days=order.order_date.weekday())] += order.quantity
            customers[order.customer] += order.total_amount
            totals = products[(order.product_id, order.product_name)]
            totals[0] += order.quantity
            totals[1] += order.total_amount

        def top(amounts: dict, count: int) -> list:
            return sorted(amounts.items(), key=lambda entry: entry[1], reverse=True)[:count]

        summary: dict[str, Any] = {
            "period": {"from": (since + timedelta(days=1)).isoformat(), "to": today.isoformat()},
            "product_id": args.product_id,
            "orders": len(orders),
            "units": sum(order.quantity for order in orders),
            "revenue": round(sum(order.total_amount for order in orders), 2),
            "orders_by_status": dict(Counter(order.status.value for order in orders)),
            "units_by_week_starting": {week.isoformat(): units for week, units in sorted(weekly.items())},
            "top_customers_by_revenue": [
                {"customer": name, "revenue": round(revenue, 2)} for name, revenue in top(customers, 5)
            ],
        }
        if args.product_id is None:
            summary["top_products_by_revenue"] = [
                {"product_id": key[0], "product_name": key[1], "units": int(totals[0]), "revenue": round(totals[1], 2)}
                for key, totals in sorted(products.items(), key=lambda entry: entry[1][1], reverse=True)[:10]
            ]
        return summary

    def _list_purchase_orders(self, args: PurchaseOrderListInput) -> dict:
        orders = self._procurement.list_orders(
            status=args.status, supplier_id=args.supplier_id, product_id=args.product_id
        )
        return {
            "matching_orders": len(orders),
            "count_by_status": dict(Counter(order.status.value for order in orders)),
            "shown": min(len(orders), args.limit),
            "orders": [order.model_dump(mode="json", exclude={"reason", "created_by"}) for order in orders[: args.limit]],
        }

    def _list_suppliers(self, args: SupplierSearchInput) -> list[dict]:
        return [
            {
                **supplier.model_dump(mode="json", exclude={"products_supplied", "email", "phone"}),
                "products_supplied": len(supplier.products_supplied),
            }
            for supplier in self._suppliers.list_suppliers(args.search)
        ]
