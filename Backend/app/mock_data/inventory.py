from datetime import timedelta

from app.mock_data import REFERENCE_DATE

MAIN, NORTH, EAST = "Main Warehouse", "North Distribution Center", "East Depot"

# (product_id, warehouse, current_stock, safety_stock, reorder_level, days since last update)
_ROWS = [
    ("P001", MAIN, 350, 500, 600, 0),
    ("P001", NORTH, 120, 100, 150, 1),
    ("P002", MAIN, 420, 150, 220, 2),
    ("P003", MAIN, 85, 80, 120, 0),
    ("P004", MAIN, 610, 200, 300, 3),
    ("P005", MAIN, 45, 120, 180, 0),
    ("P006", MAIN, 1250, 300, 450, 4),
    ("P006", EAST, 380, 100, 150, 2),
    ("P007", MAIN, 28, 60, 90, 0),
    ("P008", MAIN, 240, 90, 140, 5),
    ("P009", MAIN, 132, 110, 160, 1),
    ("P010", MAIN, 74, 40, 60, 6),
    ("P011", MAIN, 3200, 800, 1200, 3),
    ("P011", NORTH, 950, 300, 500, 2),
    ("P012", MAIN, 0, 150, 220, 1),
    ("P013", MAIN, 310, 100, 150, 7),
    ("P014", MAIN, 58, 30, 45, 4),
    ("P015", MAIN, 95, 200, 280, 0),
    ("P016", MAIN, 110, 120, 180, 1),
    ("P017", MAIN, 64, 25, 40, 8),
    ("P018", MAIN, 22, 40, 60, 0),
    ("P019", EAST, 140, 50, 80, 5),
    ("P020", EAST, 36, 30, 45, 2),
    ("P021", MAIN, 0, 0, 0, 60),
]

INVENTORY = [
    {"id": f"INV-{i:03d}", "product_id": pid, "warehouse": wh, "current_stock": stock,
     "safety_stock": safety, "reorder_level": reorder,
     "last_updated": REFERENCE_DATE - timedelta(days=age)}
    for i, (pid, wh, stock, safety, reorder, age) in enumerate(_ROWS, start=1)
]
