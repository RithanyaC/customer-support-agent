import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "ecommerce.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = _connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                city TEXT
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id TEXT,
                order_date TEXT,
                status TEXT,
                total_amount REAL,
                currency TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                item_id TEXT PRIMARY KEY,
                order_id INTEGER,
                product_name TEXT,
                category TEXT,
                quantity INTEGER,
                unit_price REAL,
                return_eligible INTEGER DEFAULT 1,
                received_date TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS shipments (
                shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                carrier TEXT,
                tracking_number TEXT,
                current_location TEXT,
                shipment_status TEXT,
                estimated_delivery TEXT,
                last_updated TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS returns (
                return_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                item_id TEXT,
                reason TEXT,
                status TEXT,
                approved INTEGER DEFAULT 0,
                rejection_reason TEXT,
                created_at TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS refunds (
                refund_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount REAL,
                status TEXT,
                expected_date TEXT,
                processed_on TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            );
            """
        )

        customer_rows = [
            ("CUST001", "Ava", "Patel", "ava.patel@example.com", "555-0101", "Seattle"),
            ("CUST002", "Leo", "Martinez", "leo.martinez@example.com", "555-0102", "Austin"),
            ("CUST003", "Nina", "Johnson", "nina.johnson@example.com", "555-0103", "Boston"),
            ("CUST004", "Omar", "Hassan", "omar.hassan@example.com", "555-0104", "Denver"),
            ("CUST005", "Priya", "Singh", "priya.singh@example.com", "555-0105", "Chicago"),
            ("CUST006", "Daniel", "Kim", "daniel.kim@example.com", "555-0106", "Portland"),
            ("CUST007", "Sofia", "Nguyen", "sofia.nguyen@example.com", "555-0107", "Miami"),
            ("CUST008", "Marcus", "Brown", "marcus.brown@example.com", "555-0108", "Phoenix"),
            ("CUST009", "Emma", "Wilson", "emma.wilson@example.com", "555-0109", "San Diego"),
            ("CUST010", "Noah", "Chen", "noah.chen@example.com", "555-0110", "Atlanta"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO customers (customer_id, first_name, last_name, email, phone, city) VALUES (?,?,?,?,?,?)",
            customer_rows,
        )

        order_ids = list(range(10001, 10051)) + list(range(10180, 10201)) + [10245, 10255, 10260, 10265]
        statuses = [
            "processing",
            "shipped",
            "in_transit",
            "out_for_delivery",
            "delivered",
            "delayed",
            "cancelled",
            "return_requested",
            "refunded",
        ]
        product_catalog = [
            ("Summit Trail Running Shoes", "footwear", 120.00),
            ("Harbor Knit Hoodie", "apparel", 80.00),
            ("Luna Ceramic Mug", "home", 22.00),
            ("Northwind Backpack", "accessories", 95.00),
            ("Aster Desk Lamp", "home", 60.00),
            ("Cascade Water Bottle", "outdoors", 28.00),
            ("Brightline Wireless Earbuds", "electronics", 110.00),
            ("Velvet Throw Blanket", "home", 70.00),
            ("Meridian Running Cap", "apparel", 30.00),
            ("Atlas Travel Tote", "accessories", 75.00),
        ]

        for idx, order_id in enumerate(order_ids):
            customer_id = customer_rows[idx % len(customer_rows)][0]
            if order_id == 10245:
                customer_id = "CUST001"
            order_date = (datetime(2025, 1, 1) + timedelta(days=idx * 3)).strftime("%Y-%m-%d")
            status = statuses[idx % len(statuses)]
            total = 0.0
            if order_id == 10245:
                status = "in_transit"
            if order_id == 10255:
                status = "delayed"
            if order_id == 10260:
                status = "refunded"
            if order_id == 10265:
                status = "cancelled"

            conn.execute(
                "INSERT OR IGNORE INTO orders (order_id, customer_id, order_date, status, total_amount, currency) VALUES (?, ?, ?, ?, ?, 'USD')",
                (order_id, customer_id, order_date, status, 0.0),
            )

            item_count = 1 if idx % 4 else 2
            item_total = 0.0
            for item_index in range(item_count):
                product_name, category, base_price = product_catalog[(idx + item_index) % len(product_catalog)]
                quantity = 1
                unit_price = round(base_price + (idx % 5) * 3.5, 2)
                item_id = f"ITEM-{10000 + idx * 10 + item_index}"
                return_eligible = 1 if category in {"footwear", "apparel", "home"} and status not in {"cancelled"} else 0
                received_date = (datetime(2025, 1, 10) + timedelta(days=idx * 2 + item_index)).strftime("%Y-%m-%d")
                conn.execute(
                    "INSERT OR IGNORE INTO order_items (item_id, order_id, product_name, category, quantity, unit_price, return_eligible, received_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (item_id, order_id, product_name, category, quantity, unit_price, return_eligible, received_date),
                )
                item_total += unit_price * quantity

            conn.execute(
                "UPDATE orders SET total_amount = ? WHERE order_id = ?",
                (round(item_total, 2), order_id),
            )

            carrier = ["UPS", "FedEx", "DHL", "USPS"][idx % 4]
            tracking_number = f"{carrier[:2].upper()}{order_id:07d}"
            current_location = ["Seattle Distribution Center", "Chicago Hub", "Denver Sorting Facility", "Local delivery route"][idx % 4]
            shipment_status = status
            if status == "processing":
                shipment_status = "processing"
            elif status in {"shipped", "in_transit", "out_for_delivery", "delayed"}:
                shipment_status = status
            elif status == "delivered":
                shipment_status = "delivered"
            elif status == "cancelled":
                shipment_status = "cancelled"
            estimated_delivery = (datetime.now() + timedelta(days=3 + (idx % 5))).strftime("%Y-%m-%d")
            if order_id == 10245:
                current_location = "Chicago Hub"
                shipment_status = "in_transit"
                estimated_delivery = "2026-10-02"
            if order_id == 10255:
                current_location = "Denver Sorting Facility"
                shipment_status = "delayed"
                estimated_delivery = "2026-10-05"
            conn.execute(
                "INSERT OR IGNORE INTO shipments (order_id, carrier, tracking_number, current_location, shipment_status, estimated_delivery, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (order_id, carrier, tracking_number, current_location, shipment_status, estimated_delivery, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )

            if status == "refunded":
                conn.execute(
                    "INSERT OR IGNORE INTO refunds (order_id, amount, status, expected_date, processed_on) VALUES (?, ?, ?, ?, ?)",
                    (order_id, round(item_total * 0.85, 2), "processed", (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d")),
                )

        # Explicit test data for 10245 and return cases
        conn.execute(
            "INSERT OR IGNORE INTO order_items (item_id, order_id, product_name, category, quantity, unit_price, return_eligible, received_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("ITEM-0001", 10245, "Summit Trail Running Shoes", "footwear", 1, 120.00, 1, "2026-09-15"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO shipments (order_id, carrier, tracking_number, current_location, shipment_status, estimated_delivery, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (10245, "UPS", "UPS1024501", "Chicago Hub", "in_transit", "2026-10-02", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.execute(
            "INSERT OR IGNORE INTO refunds (order_id, amount, status, expected_date, processed_on) VALUES (?, ?, ?, ?, ?)",
            (10260, 89.50, "processed", "2026-09-25", "2026-09-14"),
        )

        conn.commit()
    finally:
        conn.close()


def find_most_relevant_order(customer_id, message=''):
    conn = _connect()
    try:
        orders = conn.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY order_id DESC",
            (customer_id,),
        ).fetchall()
        if not orders:
            return None
        message_lower = (message or '').lower()
        for order in orders:
            items = conn.execute(
                "SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id",
                (order['order_id'],),
            ).fetchall()
            for item in items:
                product = (item['product_name'] or '').lower()
                category = (item['category'] or '').lower()
                if any(keyword in message_lower for keyword in ['shoe', 'shoes', 'footwear', 'boot']) and ('shoe' in product or category == 'footwear'):
                    return {"order_id": order['order_id'], "item_id": item['item_id']}
                if any(keyword in message_lower for keyword in ['refund', 'money back']) and order['status'] in {'refunded', 'return_requested', 'delivered'}:
                    return {"order_id": order['order_id'], "item_id": item['item_id']}
            if any(keyword in message_lower for keyword in ['return', 'refund', 'order']) and order['status'] not in {'cancelled'}:
                return {"order_id": order['order_id'], "item_id": items[0]['item_id'] if items else None}
        return {"order_id": orders[0]['order_id'], "item_id": None}
    finally:
        conn.close()


def get_customer_by_id(customer_id):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        conn.close()


def get_order_by_id(order_id, customer_id=None):
    conn = _connect()
    try:
        order_row = conn.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()
        if order_row is None:
            return None

        if customer_id is not None and order_row["customer_id"] != customer_id:
            return {
                "authorized": False,
                "order_id": order_id,
                "customer_id": order_row["customer_id"],
                "reason": "This order cannot be accessed.",
            }

        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id",
            (order_id,),
        ).fetchall()
        shipment = conn.execute(
            "SELECT * FROM shipments WHERE order_id = ? ORDER BY shipment_id DESC LIMIT 1",
            (order_id,),
        ).fetchone()
        refund = conn.execute(
            "SELECT * FROM refunds WHERE order_id = ? ORDER BY refund_id DESC LIMIT 1",
            (order_id,),
        ).fetchone()
        return {
            "authorized": True,
            "order_id": order_row["order_id"],
            "customer_id": order_row["customer_id"],
            "status": order_row["status"],
            "order_date": order_row["order_date"],
            "total_amount": order_row["total_amount"],
            "currency": order_row["currency"],
            "items": [dict(item) for item in items],
            "shipment": dict(shipment) if shipment else None,
            "refund": dict(refund) if refund else None,
        }
    finally:
        conn.close()


def get_order_items(order_id):
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id", (order_id,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_shipment(order_id):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM shipments WHERE order_id = ? ORDER BY shipment_id DESC LIMIT 1",
            (order_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_return_eligibility(order_id, item_id):
    conn = _connect()
    try:
        item = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ? AND item_id = ?",
            (order_id, item_id),
        ).fetchone()
        if item is None:
            return False, "This item is not eligible for return and cannot be processed for this order."
        if item["return_eligible"] != 1:
            return False, "This item is not eligible for return under the current policy."
        return True, "Eligible for return."
    finally:
        conn.close()


def create_return_request(order_id, item_id, reason, customer_id):
    conn = _connect()
    try:
        order = conn.execute("SELECT customer_id FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        if order is None:
            return {"success": False, "reason": "Order not found."}
        if order["customer_id"] != customer_id:
            return {"success": False, "reason": "This order cannot be accessed."}
        eligible, msg = get_return_eligibility(order_id, item_id)
        if not eligible:
            return {"success": False, "reason": msg}
        conn.execute(
            "INSERT INTO returns (order_id, item_id, reason, status, approved, rejection_reason, created_at) VALUES (?, ?, ?, 'requested', 1, NULL, ?)",
            (order_id, item_id, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return {"success": True, "status": "created", "reason": "Return request created successfully.", "order_id": order_id, "item_id": item_id}
    finally:
        conn.close()


def get_refund_details(order_id):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM refunds WHERE order_id = ? ORDER BY refund_id DESC LIMIT 1",
            (order_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


initialize_database()
