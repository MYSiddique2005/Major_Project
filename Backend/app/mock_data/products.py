def _p(id, sku, name, category, supplier_id, price, unit_cost, status="Active"):
    return {"id": id, "sku": sku, "name": name, "category": category, "supplier_id": supplier_id,
            "price": price, "unit_cost": unit_cost, "status": status}


PRODUCTS = [
    _p("P001", "LAP-PRO-14", "Laptop Pro 14", "Laptops", "S001", 1299.0, 980.0),
    _p("P002", "LAP-AIR-13", "Laptop Air 13", "Laptops", "S001", 999.0, 760.0),
    _p("P003", "MON-UHD-27", "UltraView 27\" 4K Monitor", "Monitors", "S005", 429.0, 310.0),
    _p("P004", "MON-FHD-24", "ClearView 24\" Monitor", "Monitors", "S005", 189.0, 135.0),
    _p("P005", "KEY-MEC-K8", "Mechanical Keyboard K8", "Peripherals", "S002", 89.0, 52.0),
    _p("P006", "MOU-WRL-M3", "Wireless Mouse M3", "Peripherals", "S002", 35.0, 18.0),
    _p("P007", "DOC-USB-C1", "USB-C Docking Station", "Peripherals", "S002", 159.0, 104.0),
    _p("P008", "WEB-HD-W10", "HD Webcam W10", "Peripherals", "S002", 69.0, 41.0),
    _p("P009", "RTR-AX-60", "Wi-Fi 6 Router AX60", "Networking", "S003", 179.0, 121.0),
    _p("P010", "SWT-24P-G", "24-Port Gigabit Switch", "Networking", "S003", 249.0, 172.0),
    _p("P011", "CBL-CAT6-5", "Cat6 Ethernet Cable 5m", "Networking", "S003", 9.0, 3.5),
    _p("P012", "SSD-NVM-1T", "NVMe SSD 1TB", "Storage", "S006", 119.0, 78.0),
    _p("P013", "HDD-EXT-4T", "External HDD 4TB", "Storage", "S006", 109.0, 74.0),
    _p("P014", "PRT-LSR-M2", "Laser Printer M200", "Printers", "S007", 279.0, 198.0),
    _p("P015", "TNR-M2-BLK", "Toner Cartridge M200 Black", "Printers", "S007", 59.0, 31.0),
    _p("P016", "HDS-NC-700", "Noise-Cancelling Headset H700", "Audio", "S008", 149.0, 96.0),
    _p("P017", "SPK-CONF-S5", "Conference Speakerphone S5", "Audio", "S008", 199.0, 134.0),
    _p("P018", "UPS-1500VA", "UPS 1500VA", "Power", "S009", 329.0, 240.0),
    _p("P019", "CHR-ERG-PRO", "Ergonomic Office Chair Pro", "Furniture", "S004", 349.0, 215.0),
    _p("P020", "DSK-STD-160", "Standing Desk 160cm", "Furniture", "S004", 499.0, 330.0),
    _p("P021", "LAP-CLS-15", "Laptop Classic 15", "Laptops", "S010", 749.0, 590.0, status="Discontinued"),
]
