"""What the knowledge base says.

Three kinds of passage:
  - schema: one per database table, generated from the SQLAlchemy models plus the column descriptions below;
  - access: one per role, generated from the role -> permission map;
  - definitions, rules, workflows and data notes, written here.
Thresholds and periods are taken from the constants in the code that applies them, so a passage
cannot state a different number from the one the system uses.
"""
from functools import lru_cache

from app.analytics import demand, forecasting, stock_risk, supplier_performance
from app.db.base import Base
from app.db import models  # noqa: F401  (registers the tables on Base.metadata)
from app.knowledge.base import Entry, KnowledgeBase
from app.llm.tools import MAX_ROWS
from app.models.enums import Role
from app.security.permissions import ROLE_PERMISSIONS
from app.services import analytics_service

TABLE_DESCRIPTIONS = {
    "users": "People who can sign in, with their role.",
    "suppliers": "Companies the business buys products from.",
    "products": "The product catalogue. Each product has one primary supplier.",
    "supplier_products": "Which suppliers can deliver which products (a link table).",
    "inventory": "Stock of a product in a warehouse. A product can have one record per warehouse.",
    "sales_orders": "Customer orders. Each row is one product on one order; this is the source of demand.",
    "purchase_orders": "Orders placed with suppliers to buy stock. Each row is one product.",
    "approvals": "Requests to approve a purchase order, and the decision taken.",
    "audit_logs": "A permanent record of logins, purchase-order actions and AI assistant questions.",
    "ai_scans": "Each proactive scan the AI assistant ran over the current high and critical findings.",
    "ai_insights": "Findings the AI assistant raised on its own during a scan, each with a recommendation.",
}

COLUMN_DESCRIPTIONS = {
    "users": {
        "id": "User ID, such as U001.",
        "username": "Sign-in name; also recorded as the creator or approver of purchase orders.",
        "full_name": "The person's name.",
        "email": "Email address.",
        "role": "ADMIN, INVENTORY_MANAGER, PROCUREMENT_MANAGER or EMPLOYEE; decides what the user may do.",
        "hashed_password": "Password hash. Never shown.",
        "is_active": "False for accounts that can no longer sign in.",
    },
    "suppliers": {
        "id": "Supplier ID, such as S004.",
        "name": "Supplier's company name.",
        "contact_name": "Main contact person at the supplier.",
        "email": "Contact email.",
        "phone": "Contact phone number.",
        "country": "Country the supplier delivers from.",
        "avg_delivery_days": "Stated average days from order to delivery (supplier master data). Used as the lead "
        "time only when too few real deliveries exist to measure it.",
        "delivery_reliability": "Stated percentage of orders delivered on time, 0 to 100 (supplier master data).",
        "status": "Active or Inactive. Purchase orders can only be created for Active suppliers.",
    },
    "products": {
        "id": "Product ID, such as P001.",
        "sku": "Stock-keeping unit code, unique per product.",
        "name": "Product name.",
        "category": "Product category.",
        "supplier_id": "The product's primary supplier.",
        "price": "Selling price per unit.",
        "unit_cost": "Standard purchase cost per unit. Default unit price of a new purchase order.",
        "status": "Active or Discontinued. Discontinued products are not analysed for stock risk.",
    },
    "supplier_products": {
        "supplier_id": "A supplier.",
        "product_id": "A product that supplier can deliver.",
    },
    "inventory": {
        "id": "Stock record ID, such as INV-0001.",
        "product_id": "The product held.",
        "warehouse": "Warehouse name.",
        "current_stock": "Units physically on hand now. Also called stock on hand. Cannot be negative.",
        "safety_stock": "Buffer of units kept to absorb unexpected demand or late deliveries.",
        "reorder_level": "Stock level at or below which the product should be reordered.",
        "last_updated": "Date the record was last changed.",
    },
    "sales_orders": {
        "id": "Sales order ID, such as SO-000123.",
        "customer": "Customer name.",
        "product_id": "Product sold.",
        "quantity": "Units ordered. Always positive.",
        "unit_price": "Price per unit actually charged; it can be below the product's list price.",
        "order_date": "Date the customer placed the order. Demand is counted on this date.",
        "status": "Pending, Processing, Completed or Cancelled.",
    },
    "purchase_orders": {
        "id": "Purchase order ID, such as PO-01234.",
        "supplier_id": "Supplier the order is placed with.",
        "product_id": "Product ordered.",
        "quantity": "Units ordered. Always positive.",
        "unit_price": "Agreed purchase price per unit.",
        "order_date": "Date the order was created.",
        "expected_delivery": "Date the supplier promised delivery.",
        "actual_delivery": "Date the goods arrived; empty until delivered.",
        "status": "Draft, Pending Approval, Approved, Rejected, Ordered, Delivered or Cancelled.",
        "reason": "Why the order was raised.",
        "created_by": "Who created the order.",
        "origin": "Manual, AI Assistant (drafted from a chat recommendation) or AI Insight (drafted from an insight).",
        "origin_ref": "The AI insight the draft came from, when the origin is AI Insight.",
        "ai_recommendation": "For AI drafts: the recommendation, its evidence and the server's checks when drafted.",
    },
    "approvals": {
        "id": "Approval ID, such as APR-0001.",
        "purchase_order_id": "The purchase order awaiting a decision.",
        "requested_by": "Username of whoever submitted the order for approval.",
        "requested_at": "When it was submitted.",
        "reason": "Reason given for the order.",
        "status": "Pending, Approved or Rejected.",
        "decided_by": "Username of whoever approved or rejected it.",
        "decided_at": "When the decision was taken.",
        "comment": "Comment left with the decision.",
    },
    "audit_logs": {
        "id": "Audit entry ID.",
        "timestamp": "When the event happened.",
        "user_id": "ID of the user, or 'unknown' for a failed login.",
        "username": "Username involved.",
        "action": "What was done, such as LOGIN, CREATE_PURCHASE_ORDER, APPROVE_PURCHASE_ORDER or AI_QUERY.",
        "entity": "Kind of record affected.",
        "entity_id": "ID of the record affected.",
        "status": "SUCCESS or FAILED.",
        "description": "Details of the event.",
    },
    "ai_scans": {
        "id": "Scan ID, such as SCAN-0001.",
        "started_at": "When the scan started.",
        "finished_at": "When it finished; empty while running.",
        "trigger": "'schedule' for an automatic scan, otherwise the username that started it.",
        "status": "Running, Completed or Failed.",
        "findings": "Number of high and critical findings the analytics raised at that moment.",
        "insights": "Number of insights the model recorded that passed the checks.",
        "message": "Notes on the scan, such as why it failed or which proposals were rejected.",
        "provider": "Model provider used.",
        "model": "Model that produced the insights.",
    },
    "ai_insights": {
        "id": "Insight ID, such as INS-0001.",
        "scan_id": "The scan that produced it.",
        "created_at": "When it was recorded.",
        "subject_type": "product or supplier.",
        "subject_id": "ID of the product or supplier the insight is about.",
        "subject_name": "Its name at the time.",
        "severity": "Critical, High, Medium or Low. Taken from the analytics, not from the model.",
        "headline": "The finding in one line, written by the model.",
        "explanation": "Why it matters across sales, inventory and procurement, written by the model.",
        "action": "reorder, expedite_delivery, review_supplier or monitor.",
        "product_id": "Product the action concerns.",
        "product_name": "Its name.",
        "supplier_id": "Supplier the action concerns.",
        "supplier_name": "Its name.",
        "quantity": "Units the model recommends ordering (reorder only).",
        "system_quantity": "Units the reorder rule gives, for comparison.",
        "evidence": "Facts the model relied on, each labelled with its module.",
        "checks": "Results of the server's checks: modules cited, quantity against the rule, supplier, figures.",
        "status": "New, Acknowledged, Dismissed or Superseded (replaced by a newer insight on the same subject).",
        "purchase_order_id": "The draft purchase order created from this insight, if one was.",
        "reviewed_by": "Username of whoever acknowledged or dismissed it.",
        "reviewed_at": "When that happened.",
    },
}

ROLE_DESCRIPTIONS = {
    Role.ADMIN: "Administrator. Can do everything, and is the only role that can read the audit log.",
    Role.INVENTORY_MANAGER: "Looks after stock. Can view the dashboard, sales, inventory, products and suppliers, "
    "use analytics and the AI assistant. Cannot see or create purchase orders.",
    Role.PROCUREMENT_MANAGER: "Buys stock. Can view inventory, products and suppliers, create, submit and approve "
    "purchase orders, and use analytics and the AI assistant. Cannot see sales orders.",
    Role.EMPLOYEE: "Read-only access to the dashboard, sales, inventory, products and suppliers. No analytics and "
    "no AI assistant.",
}

D, S, P, F = demand, stock_risk, supplier_performance, forecasting

WRITTEN = [
    # --- definitions ------------------------------------------------------------------------
    Entry("def.stock-on-hand", "Stock on hand (current stock)", "definition",
          "Stock on hand is the number of units physically in the warehouse now (inventory.current_stock). For a "
          "product held in several warehouses it is the sum over all of them. It does not include units on order.",
          "current_stock on_hand inventory level quantity available units in stock how many do we have"),
    Entry("def.safety-stock", "Safety stock", "definition",
          "Safety stock is a buffer of units kept to cover unexpected demand or a late delivery "
          "(inventory.safety_stock). Stock below safety stock means the buffer is being used; it is a warning, not "
          "yet a stockout. A product at or below half its safety stock has Critical stock status.",
          "buffer stock minimum stock safety level reserve"),
    Entry("def.reorder-level", "Reorder level and reorder point", "definition",
          "Two related figures. The reorder level (inventory.reorder_level) is stored on each stock record and "
          "drives the stock status shown on the Inventory page: stock at or below it is Low Stock. The reorder "
          "point is calculated by the analytics from current demand: average daily demand x lead time + safety "
          "stock. A reorder is suggested when stock plus units already on order is at or below the reorder point.",
          "reorder threshold when to order trigger min level ROP"),
    Entry("def.days-of-cover", "Days of cover and projected stockout date", "definition",
          "Days of cover is how long the stock on hand would last at the current rate of sale: stock on hand / "
          "average daily demand. The projected stockout date is today plus that many days. Both are empty when the "
          "product is not selling. They ignore deliveries that are on the way; the risk level takes those into "
          "account separately.",
          "days of supply runway how long will stock last run out date stockout date coverage"),
    Entry("def.avg-daily-demand", "Average daily demand and demand trend", "definition",
          f"Average daily demand is units sold per day over the last {D.TREND_WINDOW_DAYS} days, counting every "
          f"sales order except Cancelled ones on its order date. The demand trend is the percentage change in units "
          f"against the {D.TREND_WINDOW_DAYS} days before that. No trend is given unless both periods have at least "
          f"{D.MIN_ORDERS_FOR_TREND} orders, because a percentage on very few orders is misleading. Demand counts as "
          f"rising sharply at +{S.RISING_DEMAND_PCT:g}% or more.",
          "sales rate velocity run rate demand increase growth rising falling consumption units per day"),
    Entry("def.lead-time", "Lead time", "definition",
          f"Lead time is the number of days from placing a purchase order to receiving the goods. The analytics use "
          f"the observed lead time, the average over the supplier's actual deliveries, when the supplier has at least "
          f"{analytics_service.MIN_DELIVERIES_FOR_OBSERVED_LEAD_TIME} deliveries; otherwise the supplier's stated "
          f"average delivery days. Results say which was used ('observed deliveries' or 'supplier master data'). "
          f"Lead time is a property of the product's primary supplier.",
          "delivery time replenishment time how long does delivery take supplier lead days avg_delivery_days"),
    Entry("def.units-on-order", "Units on order, overdue units and units awaiting approval", "definition",
          "Three groups of stock that has been requested but is not on hand. Units on order (inbound units) are on "
          "purchase orders with status Ordered, not yet delivered, whose expected delivery date is today or later. "
          "Overdue units are on Ordered purchase orders whose expected delivery date has passed without delivery; "
          "their arrival date is unknown. Units awaiting approval are on purchase orders that are Pending Approval "
          "or Approved, which have not been placed with the supplier. Draft orders count for nothing.",
          "inbound incoming in transit open purchase orders pipeline late delivery overdue pending"),
    Entry("def.on-time-rate", "On-time rate, delay and delay trend of a supplier", "definition",
          f"For each delivered purchase order, the delay is the number of days the goods arrived after the expected "
          f"delivery date; early or on-time arrivals count as 0. The on-time rate is the percentage of deliveries "
          f"with a delay of 0. Average delay and longest delay are over all deliveries. The delay trend compares the "
          f"orders that were due in the last {P.TREND_WINDOW_DAYS} days with those due in the {P.TREND_WINDOW_DAYS} "
          f"days before: worsening or improving if the average delay differs by more than "
          f"{P.TREND_TOLERANCE_DAYS:g} days, otherwise stable. An order still overdue counts with its delay so far, "
          f"and each period needs at least {P.MIN_ORDERS_PER_TREND_WINDOW} orders. These are measured from purchase-order history and can differ "
          f"from the stated delivery_reliability in the supplier's master data.",
          "supplier reliability punctuality late deliveries lateness delivery performance OTD on time delivery"),
    Entry("def.revenue", "Revenue, total sales and average order value", "definition",
          "Revenue (total sales) is the sum of quantity x unit price over sales orders, excluding Cancelled orders. "
          "It is before tax. Average order value is revenue divided by the number of non-cancelled orders. Each "
          "sales order row is one product, so an 'order' here is one order line.",
          "turnover sales value income AOV total amount order value"),
    Entry("def.margin", "Price, unit cost and gross margin", "definition",
          "Price is what a unit sells for (products.price); unit cost is the standard cost of buying a unit "
          "(products.unit_cost). Gross margin per unit is price minus unit cost, and as a percentage it is that "
          "difference divided by price. A sales order can carry a unit price below the list price.",
          "profit markup profitability cost price selling price"),
    Entry("def.forecast-error", "Forecast method and backtest error (WAPE)", "definition",
          f"Demand forecasts are weekly. Two methods exist: moving_average, the mean of the last "
          f"{F.MOVING_AVERAGE_WEEKS} weeks held flat, and linear_trend, a straight line fitted to the last "
          f"{F.TREND_WEEKS} weeks. Each is tested by forecasting each of the last {F.BACKTEST_WEEKS} weeks from the "
          f"weeks before it. The backtest error is the weighted absolute percentage error (WAPE): total absolute "
          f"error divided by total actual units, so 0.2 means forecasts were off by 20% of demand. The method with "
          f"the lower error is used. The forecast uses {analytics_service.HISTORY_WEEKS} weeks of history and has no "
          f"seasonality.",
          "prediction accuracy forecasting model how reliable is the forecast error rate MAPE"),
    # --- rules ------------------------------------------------------------------------------
    Entry("rule.stock-status", "Stock status rule (In Stock, Low Stock, Critical, Out of Stock)", "rule",
          "Stock status is set per stock record by the first rule that matches: Out of Stock when current stock is "
          "0; Critical when current stock is at or below half the safety stock; Low Stock when current stock is at "
          "or below the reorder level; otherwise In Stock. Low Stock is common and often normal: it means a reorder "
          "is due or already on its way, not that customers are being turned away.",
          "inventory status low stock critical out of stock classification meaning"),
    Entry("rule.stockout-risk", "Stockout risk level rule (Critical, High, Medium, Low)", "rule",
          f"Stockout risk is assessed per active product from sales, inventory and procurement together. The first "
          f"rule that matches gives the level. Critical: nothing on hand while the product is still selling. High: "
          f"either days of cover is less than the lead time, or stock is below safety stock while demand is up "
          f"{S.RISING_DEMAND_PCT:g}% or more; and in both cases no delivery on order is due before the projected "
          f"stockout date. Medium: stock is below safety stock; or days of cover is less than the lead time plus "
          f"{S.REVIEW_BUFFER_DAYS} days and no delivery is due in time; or days of cover is less than the lead time "
          f"and the delivery it relies on comes from a supplier whose delivery risk is High. Low: none of these, "
          f"which includes stock that is short but covered by a delivery due before it runs out from a supplier "
          f"that is not high risk. Overdue units do not count as due in time. Stockout risk is different from stock "
          f"status, which looks only at the stock record.",
          "risk assessment why is a product at risk running out shortage risk classification high risk critical"),
    Entry("rule.reorder-suggestion", "Reorder suggestion rule (how much to order)", "rule",
          f"A reorder is suggested only when stock on hand + units on order + overdue units + units awaiting "
          f"approval is at or below the reorder point (average daily demand x lead time + safety stock). The "
          f"suggested quantity brings that total up to the target level: average daily demand x (lead time + "
          f"{S.REVIEW_PERIOD_DAYS} days review period) + safety stock, rounded up to a multiple of "
          f"{S.ORDER_MULTIPLE}. The suggested supplier is the product's primary supplier if Active; otherwise the "
          f"Active supplier of that product with the highest delivery reliability. A suggestion creates nothing; a "
          f"user with procurement rights can open it as a draft purchase order.",
          "order quantity replenishment how many units should we order purchase recommendation restock"),
    Entry("rule.supplier-risk", "Supplier delivery risk rule (High, Medium, Low)", "rule",
          f"Supplier risk comes from purchase-order history; the first rule that matches gives the level. High: an "
          f"open order is overdue, or fewer than 50% of deliveries were on time, or delays are worsening and average "
          f"2 days or more. Medium: average delay is 1 day or more, or fewer than 60% of deliveries were on time. "
          f"Low: otherwise, including suppliers with no deliveries. The on-time percentage is only used once a "
          f"supplier has at least {P.MIN_DELIVERIES_FOR_RATE} deliveries, so one late delivery cannot make a "
          f"supplier High.",
          "vendor risk unreliable supplier late supplier rating supplier score"),
    Entry("rule.what-if", "What-if projection assumptions", "rule",
          "A what-if projection moves stock forward day by day. It assumes demand is constant at the stated daily "
          "rate; demand that cannot be served from stock is lost, not back-ordered; deliveries arrive in full on "
          "their due date; and only purchase orders already placed with a supplier (status Ordered) count as "
          "incoming, so drafts and orders awaiting approval do not. Overdue units are left out because their "
          "arrival date is unknown. A new order in the scenario arrives after the lead time. Nothing is saved.",
          "scenario simulation projection what happens if demand rises delivery is late"),
    Entry("rule.po-validation", "Purchase order validation rules", "rule",
          "A purchase order is accepted only if: the supplier exists and is Active; the product exists; the "
          "supplier supplies that product; quantity is positive and at most 100,000; unit price is positive; and "
          "the expected delivery date is not before the order date. If no unit price is given it defaults to the "
          "product's unit cost. If no expected delivery date is given it defaults to today plus the supplier's "
          "average delivery days, rounded up. The same rules apply to every order, whoever or whatever drafted it.",
          "create purchase order requirements constraints checks valid order"),
    Entry("rule.ai-assistant", "What the AI assistant may and may not do", "rule",
          f"The AI assistant answers from read-only tools and the knowledge base. It uses only the tools the user's "
          f"role permits, so it cannot show data the user could not open themselves. The one thing it can create is "
          f"a draft purchase order, and only for a user who may create purchase orders and has asked for it. It "
          f"cannot edit, submit, approve, cancel or place anything. List tools return at most {MAX_ROWS} rows per "
          f"call. The figures in an answer are checked against what the tools returned, the passages supplied and "
          f"the question: an answer that states figures although no tool was called is sent back to be corrected, "
          f"and any figure that still cannot be traced is listed under the answer as unverified. Statements about a "
          f"product or supplier (below safety stock, demand rising, a delivery due in time, a risk level) are "
          f"checked against the data too; a contradicted statement is sent back once and, if it remains, is listed "
          f"under the answer. Every question is "
          f"written to the audit log with the tools used.",
          "assistant limits capabilities permissions chatbot LLM"),
    Entry("rule.ai-insights", "Proactive AI insights and how recommendations are checked", "rule",
          "The AI assistant scans the data on a schedule and on request. The analytics decide what is wrong: only "
          "High and Critical stockout or supplier findings are analysed, the most severe first. For each, the "
          "model writes an insight: a headline, an explanation connecting sales, inventory and procurement, a "
          "recommended action (reorder, expedite_delivery, review_supplier or monitor) and its evidence by module. "
          "The server then checks it: severity is set from the analytics; a reorder quantity is compared with the "
          "quantity the reorder rule gives; the supplier must be able to supply the product; and every figure in "
          "the text is looked up among the system's figures; and every statement such as 'below safety stock' or "
          "'demand rising' is checked against the data, and an insight that contradicts it is sent back to be "
          "corrected before it is stored. An insight is New until a user acknowledges or "
          "dismisses it. It is superseded when its subject is analysed again, and also, whether New or "
          "Acknowledged, once the analytics no longer flag its subject. "
          "Recommendations made in the chat pass the same checks. An insight creates no order by itself; a user "
          "can turn a reorder insight into a draft purchase order.",
          "proactive monitoring alerts scan insight recommendation verification checked hallucination dashboard"),
    # --- workflows --------------------------------------------------------------------------
    Entry("flow.purchase-order", "Purchase order lifecycle and statuses", "workflow",
          "A purchase order starts as Draft. Only a Draft can be edited, deleted or submitted. Submitting sets it "
          "to Pending Approval and creates an approval request. An approver then sets it to Approved or Rejected; "
          "that decision is final. Ordered means the order has been placed with the supplier and goods are "
          "expected; Delivered means the goods arrived and the actual delivery date is recorded; Cancelled means it "
          "was withdrawn. Only Ordered purchase orders count as incoming stock.",
          "PO status draft pending approval approved rejected ordered delivered cancelled process steps"),
    Entry("flow.approval", "Approval rules", "workflow",
          "Creating, editing and submitting purchase orders needs the procurement:create permission; approving or "
          "rejecting needs procurement:approve. An approval can be decided once, while it is Pending and its "
          "purchase order is Pending Approval. The decision, the decider and an optional comment are stored, and "
          "the purchase order and the audit entry are saved together. Separation of duties is enforced: the user "
          "who created or submitted a purchase order cannot approve it, so a second approver is needed; they may "
          "still reject it. This includes a draft the AI assistant prepared for them.",
          "who can approve sign off authorise authorize approval center"),
    Entry("flow.ai-draft", "AI-drafted purchase orders (controlled actions)", "workflow",
          "A reorder recommendation from the AI assistant or an AI insight can be turned into a draft purchase "
          "order, by the user clicking 'Create draft purchase order' or asking the assistant to draft it. The "
          "steps are fixed. 1: the recommendation is checked on the server against the reorder rule, the supplier "
          "and the system's figures. 2: a Draft is created through the same validation as any purchase order, "
          "marked with its origin (AI Assistant or AI Insight) and carrying the recommendation, its evidence and "
          "the check results. 3: a user with procurement:create reviews it, may edit it, and submits it. 4: a user "
          "with procurement:approve, other than the one who created or submitted it, approves or rejects it. Only a "
          "user who may create purchase orders can have "
          "one drafted. The AI cannot submit, approve or place an order, and at most 3 drafts are created for one "
          "chat message. If the user names a supplier that cannot supply the product, the draft is refused and the "
          "assistant may not draft from a different supplier in the same message; the user has to ask for that. A quantity that differs from the reorder rule does not block the draft but is flagged on "
          "it for the reviewer and approver. Every step is in the audit log.",
          "AI purchase order automatic order assistant creates order human approval human in the loop draft PO"),
    Entry("flow.sales-order", "Sales order statuses", "workflow",
          "A sales order is Pending while it waits for stock or processing, Processing once shipped and on its way "
          "to the customer, and Completed once delivered. Cancelled orders are excluded from revenue and from "
          "demand. Sales orders are read-only in this system.",
          "order status pending processing completed cancelled shipped delivered fulfilment"),
    # --- data notes -------------------------------------------------------------------------
    Entry("data.identifiers", "Record identifiers and how the modules link", "data",
          "Products have IDs like P001, suppliers S001, sales orders SO-000001, purchase orders PO-00001, stock "
          "records INV-0001. The product ID links the three modules: sales_orders.product_id gives demand, "
          "inventory.product_id gives stock, and purchase_orders.product_id gives incoming supply. "
          "products.supplier_id and purchase_orders.supplier_id link to the supplier.",
          "ID format keys join relationship how are sales inventory procurement connected cross module"),
    Entry("data.dataset", "Where the data comes from and what is simulated", "data",
          "When the Wide World Importers dataset is loaded (products with SKUs like WWI-0001), products, suppliers, "
          "customers, prices, costs and sales orders are records of a fictional wholesale importer from Microsoft's "
          "sample database. Purchase orders, delivery dates, stock levels, safety stock, reorder levels and sales "
          "order statuses are simulated from those sales with a reorder-point policy and assumed supplier "
          "reliability. Dates were moved forward so the last day of the data is the day it was loaded. There is one "
          "warehouse (Main Warehouse) and one currency (US dollars), and each product has one supplier. Figures "
          "about supply should be described as simulated.",
          "source real or fake data origin synthetic currency warehouse how reliable is the data"),
    Entry("data.limits", "Limits of the figures", "data",
          "Projections assume constant demand. Forecasts are simple statistical methods without seasonality. "
          "Alerts and risk levels are computed when asked for, not on a schedule, so they reflect the data at that "
          "moment. Tax is not included in any amount. The application holds the most recent 12 months of sales "
          "and purchase orders unless more were loaded.",
          "accuracy caveats limitations assumptions history period"),
]


def _schema_entries() -> list[Entry]:
    entries = []
    for table in Base.metadata.sorted_tables:
        columns = COLUMN_DESCRIPTIONS[table.name]
        lines = [TABLE_DESCRIPTIONS[table.name], "Columns:"]
        for column in table.columns:
            notes = []
            if column.primary_key:
                notes.append("primary key")
            for key in column.foreign_keys:
                notes.append(f"refers to {key.column.table.name}.{key.column.name}")
            suffix = f" ({', '.join(notes)})" if notes else ""
            lines.append(f"- {column.name}{suffix}: {columns[column.name]}")
        entries.append(Entry(
            f"schema.{table.name}", f"Table {table.name}", "schema", "\n".join(lines),
            f"{table.name.replace('_', ' ')} table columns fields database schema",
        ))
    return entries


def _access_entries() -> list[Entry]:
    return [
        Entry(
            f"access.{role.value.lower()}", f"Role {role.value}", "access",
            f"{ROLE_DESCRIPTIONS[role]} Permissions: {', '.join(sorted(ROLE_PERMISSIONS[role]))}.",
            f"{role.value.replace('_', ' ')} role permissions access rights who can see allowed",
        )
        for role in Role
    ]


@lru_cache
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase(_schema_entries() + _access_entries() + WRITTEN)
