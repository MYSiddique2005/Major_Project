from datetime import date, timedelta

import pytest

from app.analytics import forecasting, simulation, stock_risk, supplier_performance
from app.analytics.demand import demand_stats, weekly_units
from app.models.entities import PurchaseOrder, SalesOrder
from app.models.enums import RiskLevel
from tests.conftest import API

TODAY = date(2026, 6, 1)


# --- Pure analytics functions (no database, no HTTP) --------------------------


def _sale(days_ago: int, quantity: int, status: str = "Completed") -> SalesOrder:
    return SalesOrder(
        id=f"SO-{days_ago}-{quantity}", customer="Test", product_id="P001", quantity=quantity, unit_price=10.0,
        order_date=TODAY - timedelta(days=days_ago), status=status,
    )


def _po(ordered_days_ago: int, lead: int, late: int | None, status: str = "Delivered") -> PurchaseOrder:
    order_date = TODAY - timedelta(days=ordered_days_ago)
    expected = order_date + timedelta(days=lead)
    return PurchaseOrder(
        id=f"PO-{ordered_days_ago}", supplier_id="S001", product_id="P001", quantity=10, unit_price=1.0,
        order_date=order_date, expected_delivery=expected,
        actual_delivery=expected + timedelta(days=late) if late is not None else None,
        status=status, created_by="test",
    )


def test_demand_stats_average_and_trend():
    orders = [_sale(d, 10) for d in range(1, 29)] + [_sale(d, 5) for d in range(29, 57)]
    stats = demand_stats(orders, TODAY)
    assert stats.avg_daily_demand == 10
    assert stats.previous_avg_daily_demand == 5
    assert stats.trend_pct == 100.0


def test_demand_stats_ignores_cancelled_and_today():
    orders = [_sale(1, 28), _sale(2, 500, status="Cancelled"), _sale(0, 999)]
    assert demand_stats(orders, TODAY).avg_daily_demand == 1


def test_trend_needs_enough_orders():
    assert demand_stats([_sale(1, 10), _sale(40, 5)], TODAY).trend_pct is None


def test_weekly_units_buckets_end_yesterday():
    buckets = weekly_units([_sale(1, 3), _sale(7, 4), _sale(8, 5)], TODAY, weeks=2)
    assert buckets == [(TODAY - timedelta(days=14), 5), (TODAY - timedelta(days=7), 7)]


def test_forecast_methods():
    assert forecasting.moving_average([1, 1, 10, 20, 30, 40], 2) == [25, 25]
    assert forecasting.linear_trend([10, 20, 30, 40], 2) == pytest.approx([50, 60])
    assert forecasting.linear_trend([40, 30, 20, 10], 3) == pytest.approx([0, 0, 0])  # never negative


def test_backtest_prefers_trend_for_trending_series():
    rising = [float(10 * i) for i in range(1, 21)]
    assert forecasting.backtest_wape(rising, forecasting.linear_trend) == 0
    assert forecasting.backtest_wape(rising, forecasting.moving_average) > 0
    assert forecasting.choose_method(rising) == "linear_trend"
    assert forecasting.choose_method([5.0, 5.0]) == "moving_average"  # too short to backtest


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        (dict(on_hand=0, safety_stock=50, avg_daily_demand=5, lead_time_days=7), RiskLevel.CRITICAL),
        # 4 days of cover, 7-day lead time
        (dict(on_hand=20, safety_stock=10, avg_daily_demand=5, lead_time_days=7), RiskLevel.HIGH),
        # below safety stock with demand up 30%
        (dict(on_hand=90, safety_stock=100, avg_daily_demand=2, demand_trend_pct=30, lead_time_days=7), RiskLevel.HIGH),
        # same as the 4-day case, but a delivery arrives before stock runs out
        (
            dict(on_hand=20, safety_stock=10, avg_daily_demand=5, lead_time_days=7, inbound_units=100,
                 next_inbound_date=TODAY + timedelta(days=2)),
            RiskLevel.MEDIUM,
        ),
        (dict(on_hand=90, safety_stock=100, avg_daily_demand=2, lead_time_days=7), RiskLevel.MEDIUM),
        (dict(on_hand=500, safety_stock=100, avg_daily_demand=2, lead_time_days=7), RiskLevel.LOW),
        (dict(on_hand=500, safety_stock=100, avg_daily_demand=0, lead_time_days=7), RiskLevel.LOW),
    ],
)
def test_stock_risk_levels(position, expected):
    position.setdefault("demand_trend_pct", None)
    assert stock_risk.assess(stock_risk.StockPosition(**position), TODAY).level == expected


def test_stock_risk_evidence_and_suggestion():
    risk = stock_risk.assess(
        stock_risk.StockPosition(on_hand=20, safety_stock=50, avg_daily_demand=5, demand_trend_pct=None, lead_time_days=6),
        TODAY,
    )
    assert risk.days_of_cover == 4
    assert risk.projected_stockout_date == TODAY + timedelta(days=4)
    assert risk.reorder_point == 80  # 5/day x 6 days + 50 safety
    assert risk.suggested_order_quantity == 130  # 5 x (6 + 14) + 50 - 20
    assert any("below safety stock" in d for d in risk.drivers)


def test_no_suggestion_when_pipeline_covers_reorder_point():
    risk = stock_risk.assess(
        stock_risk.StockPosition(on_hand=20, safety_stock=50, avg_daily_demand=5, demand_trend_pct=None,
                                 lead_time_days=6, awaiting_approval_units=200),
        TODAY,
    )
    assert risk.suggested_order_quantity == 0


def test_supplier_performance_levels():
    reliable = supplier_performance.assess([_po(60, 5, 0), _po(40, 5, 0), _po(20, 5, 0)], TODAY)
    assert (reliable.level, reliable.on_time_rate, reliable.avg_lead_time_days) == (RiskLevel.LOW, 100.0, 5.0)

    worsening = supplier_performance.assess([_po(90, 5, 0), _po(70, 5, 1), _po(50, 5, 4), _po(30, 5, 6)], TODAY)
    assert (worsening.level, worsening.delay_trend) == (RiskLevel.HIGH, "worsening")

    one_late = supplier_performance.assess([_po(30, 5, 2)], TODAY)
    assert one_late.level == RiskLevel.MEDIUM  # a single late delivery is not enough for High

    overdue = supplier_performance.assess([_po(20, 5, None, status="Ordered")], TODAY)
    assert (overdue.level, overdue.overdue_orders) == (RiskLevel.HIGH, 1)

    assert supplier_performance.assess([], TODAY).level == RiskLevel.LOW


def test_simulation_projection():
    arrival = TODAY + timedelta(days=8)
    result = simulation.project(
        on_hand=50, daily_demand=10, arrivals={arrival: 100}, safety_stock=20, today=TODAY, horizon_days=10
    )
    assert result.stockout_date == TODAY + timedelta(days=5)
    assert result.unmet_demand_units == 20  # days 6 and 7 cannot be served
    assert result.ending_stock == 70  # 100 arrive on day 8, then three days of demand
    assert min(stock for _, stock in result.points) == 0  # never negative
    assert len(result.points) == 11


# --- API ------------------------------------------------------------------------


def test_stock_risk_endpoint(client, auth):
    headers = auth("inventory")
    items = client.get(f"{API}/analytics/stock-risk", headers=headers).json()
    by_id = {item["product_id"]: item for item in items}

    assert "P021" not in by_id  # discontinued products are not analysed
    assert by_id["P012"]["risk_level"] == "Critical"  # out of stock
    assert by_id["P001"]["risk_level"] == "High"
    assert by_id["P001"]["demand_trend_pct"] > 15
    assert by_id["P001"]["on_hand"] == 470  # both warehouses
    assert by_id["P001"]["awaiting_approval_units"] == 800
    assert by_id["P005"]["overdue_inbound_units"] == 300
    assert all(item["drivers"] for item in items if item["risk_level"] != "Low")

    order = ["Critical", "High", "Medium", "Low"]
    assert [order.index(i["risk_level"]) for i in items] == sorted(order.index(i["risk_level"]) for i in items)

    high = client.get(f"{API}/analytics/stock-risk", params={"level": "High"}, headers=headers).json()
    assert high and all(item["risk_level"] == "High" for item in high)


def test_reorder_suggestion_names_an_active_supplier(client, auth):
    item = client.get(f"{API}/analytics/stock-risk/P016", headers=auth("procurement")).json()
    assert item["suggested_order_quantity"] > 0
    assert item["suggested_supplier_id"] == "S008"


def test_stock_risk_not_found(client, auth):
    headers = auth("admin")
    assert client.get(f"{API}/analytics/stock-risk/P999", headers=headers).status_code == 404
    assert client.get(f"{API}/analytics/stock-risk/P021", headers=headers).status_code == 404  # discontinued


def test_forecast_endpoint(client, auth):
    headers = auth("admin")
    forecast = client.get(f"{API}/analytics/forecast/P001", params={"horizon_weeks": 6}, headers=headers).json()
    assert len(forecast["history"]) == 26
    assert len(forecast["forecast"]) == 6
    assert forecast["method_selection"] == "lowest backtest error"
    assert all(point["units"] >= 0 for point in forecast["forecast"])

    requested = client.get(
        f"{API}/analytics/forecast/P001", params={"method": "moving_average"}, headers=headers
    ).json()
    assert requested["method"] == "moving_average"
    assert len({point["units"] for point in requested["forecast"]}) == 1  # flat

    assert client.get(f"{API}/analytics/forecast/P001", params={"horizon_weeks": 99}, headers=headers).status_code == 422


def test_supplier_performance_endpoint(client, auth):
    suppliers = client.get(f"{API}/analytics/supplier-performance", headers=auth("admin")).json()
    by_id = {s["supplier_id"]: s for s in suppliers}
    assert by_id["S002"]["risk_level"] == "High"
    assert by_id["S002"]["overdue_orders"] == 1
    assert by_id["S002"]["delay_trend"] == "worsening"
    assert by_id["S001"]["risk_level"] == "Low"
    assert by_id["S010"]["deliveries_analyzed"] == 0


def test_alerts_are_urgent_and_attributed_to_rules(client, auth):
    alerts = client.get(f"{API}/analytics/alerts", headers=auth("admin")).json()
    assert alerts
    assert all(a["severity"] in ("High", "Critical") for a in alerts)
    assert all(a["source"] == "Rule-based analytics" for a in alerts)
    assert {"stock-P012", "supplier-S002"} <= {a["id"] for a in alerts}


def test_what_if(client, auth):
    headers = auth("procurement")
    unchanged = client.post(f"{API}/analytics/what-if", json={"product_id": "P001"}, headers=headers).json()
    assert unchanged["baseline"] == unchanged["scenario"]
    assert len(unchanged["baseline"]["points"]) == 61

    worse = client.post(
        f"{API}/analytics/what-if", json={"product_id": "P001", "demand_change_pct": 50}, headers=headers
    ).json()
    assert worse["scenario"]["days_until_stockout"] < worse["baseline"]["days_until_stockout"]

    reordered = client.post(
        f"{API}/analytics/what-if", json={"product_id": "P001", "order_quantity": 2000}, headers=headers
    ).json()
    assert reordered["scenario"]["stockout_date"] is None
    assert reordered["scenario"]["unmet_demand_units"] == 0

    # A what-if never creates anything.
    orders = client.get(f"{API}/procurement", params={"product_id": "P001"}, headers=headers).json()
    assert all(po["quantity"] != 2000 for po in orders)

    assert client.post(f"{API}/analytics/what-if", json={"product_id": "P999"}, headers=headers).status_code == 404
    assert client.post(
        f"{API}/analytics/what-if", json={"product_id": "P001", "horizon_days": 1}, headers=headers
    ).status_code == 422


def test_analytics_rbac(client, auth):
    assert client.get(f"{API}/analytics/stock-risk").status_code == 401
    assert client.get(f"{API}/analytics/stock-risk", headers=auth("employee")).status_code == 403
    assert client.post(
        f"{API}/analytics/what-if", json={"product_id": "P001"}, headers=auth("employee")
    ).status_code == 403
    assert client.get(f"{API}/analytics/alerts", headers=auth("inventory")).status_code == 200
