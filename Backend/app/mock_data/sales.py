"""Generated sales history: one year of orders per product, deterministic (seeded).

Each product has a typical daily demand and order size. Orders are emitted when
the accumulated expected demand reaches the next order's quantity, so volumes
track the intended rates closely. Laptop Pro 14 (P001) demand ramps up over the
last eight weeks to give the analytics layer a rising trend to detect.
"""
import math
import random
from datetime import timedelta

from app.mock_data import REFERENCE_DATE
from app.mock_data.products import PRODUCTS

CUSTOMERS = [
    "Northwind Traders", "Contoso Retail", "Meridian Consulting", "Bluepeak Software",
    "Harbor Logistics", "Summit Financial Group", "Orchard Health Clinics", "Atlas Engineering",
    "Lakeside University", "Vertex Media", "Pioneer Manufacturing", "Cedar Grove Schools",
]

HISTORY_DAYS = 365

# product_id: (average units sold per day, smallest order, largest order)
DEMAND_PROFILE = {
    "P001": (9.0, 4, 20),
    "P002": (5.0, 4, 24),
    "P003": (2.5, 4, 20),
    "P004": (6.0, 10, 50),
    "P005": (7.0, 10, 60),
    "P006": (15.0, 20, 120),
    "P007": (3.0, 5, 30),
    "P008": (3.0, 5, 30),
    "P009": (3.5, 5, 30),
    "P010": (1.0, 2, 12),
    "P011": (60.0, 100, 600),
    "P012": (6.0, 10, 50),
    "P013": (2.5, 5, 25),
    "P014": (0.8, 2, 10),
    "P015": (8.0, 10, 60),
    "P016": (4.0, 5, 40),
    "P017": (1.0, 2, 12),
    "P018": (1.2, 2, 12),
    "P019": (1.5, 2, 15),
    "P020": (0.8, 2, 10),
}

RAMP_PRODUCT, RAMP_DAYS, RAMP_PEAK = "P001", 56, 1.7


def _multiplier(product_id: str, days_ago: int) -> float:
    seasonal = 1 + 0.08 * math.sin(2 * math.pi * days_ago / 365)
    if product_id == RAMP_PRODUCT and days_ago < RAMP_DAYS:
        return seasonal * (1 + (RAMP_PEAK - 1) * (RAMP_DAYS - days_ago) / RAMP_DAYS)
    return seasonal


def _status(rng: random.Random, days_ago: int) -> str:
    if days_ago <= 2:
        return rng.choice(["Pending", "Pending", "Processing"])
    if days_ago <= 7:
        return rng.choice(["Processing", "Processing", "Completed"])
    return "Cancelled" if rng.random() < 0.03 else "Completed"


def _generate() -> list[dict]:
    rng = random.Random(42)
    prices = {p["id"]: p["price"] for p in PRODUCTS}
    orders = []
    for product_id, (daily_units, smallest, largest) in DEMAND_PROFILE.items():
        backlog = rng.uniform(0, smallest)
        next_quantity = rng.randint(smallest, largest)
        for days_ago in range(HISTORY_DAYS, -1, -1):
            backlog += daily_units * _multiplier(product_id, days_ago)
            while backlog >= next_quantity:
                backlog -= next_quantity
                orders.append({
                    "customer": rng.choice(CUSTOMERS),
                    "product_id": product_id,
                    "quantity": next_quantity,
                    "unit_price": prices[product_id],
                    "order_date": REFERENCE_DATE - timedelta(days=days_ago),
                    "status": _status(rng, days_ago),
                })
                next_quantity = rng.randint(smallest, largest)
    orders.sort(key=lambda o: (o["order_date"], o["product_id"]))
    for i, order in enumerate(orders, start=1001):
        order["id"] = f"SO-{i}"
    return orders


SALES = _generate()
