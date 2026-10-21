import sqlite3
import random
from datetime import datetime, timedelta
import os

def generate_database(db_path="data/ecommerce_logistics.db", num_orders=2500):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        customer_name TEXT,
        city TEXT,
        state TEXT,
        segment TEXT,
        signup_date DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE products (
        product_id TEXT PRIMARY KEY,
        category TEXT,
        product_name TEXT,
        unit_price REAL,
        cost_of_goods REAL,
        weight_kg REAL,
        stock_quantity INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        order_status TEXT,
        order_date TIMESTAMP,
        delivered_date TIMESTAMP,
        estimated_delivery_date TIMESTAMP,
        total_amount REAL,
        freight_cost REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        product_id TEXT,
        quantity INTEGER,
        unit_price REAL,
        subtotal REAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE deliveries (
        delivery_id TEXT PRIMARY KEY,
        order_id TEXT,
        carrier TEXT,
        status TEXT,
        transit_days INTEGER,
        is_delayed BOOLEAN,
        delay_days INTEGER,
        customer_rating INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    """)

    # Seed Customers
    cities = [("Mumbai", "MH"), ("Bengaluru", "KA"), ("Delhi", "DL"), ("Pune", "MH"), 
              ("Hyderabad", "TS"), ("Chennai", "TN"), ("Kolkata", "WB"), ("Ahmedabad", "GJ")]
    segments = ["Enterprise", "SMB", "Consumer", "D2C Direct"]
    
    customers = []
    base_date = datetime(2025, 1, 1)
    for i in range(1, 601):
        c_id = f"CUST-{i:04d}"
        c_name = f"Client {i}"
        city, state = random.choice(cities)
        segment = random.choice(segments)
        signup = (base_date + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        customers.append((c_id, c_name, city, state, segment, signup))
    
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers)

    # Seed Products
    categories = {
        "Consumer Electronics": [("Wireless Noise-Canceling Headphones", 149.99, 65.0, 0.4), 
                                 ("Smart Fitness Watch Pro", 199.99, 85.0, 0.2), 
                                 ("Ultra-Slim 65W GaN Charger", 45.0, 15.0, 0.15)],
        "Office & Workspace": [("Ergonomic Mesh Chair", 249.0, 110.0, 14.5), 
                               ("Motorized Standing Desk 55-inch", 399.0, 180.0, 32.0),
                               ("Mechanical Keyboard RGB", 89.0, 32.0, 0.9)],
        "Logistics & Packaging": [("Eco-friendly Bubble Mailers (100pk)", 35.0, 12.0, 2.5), 
                                  ("Heavy Duty Packing Tape 6-Rolls", 22.0, 6.5, 1.2)],
        "Industrial Hardware": [("Precision Digital Caliper", 42.0, 14.0, 0.35), 
                                ("Thermal Imaging Camera Portable", 499.0, 210.0, 0.85)]
    }

    products = []
    p_counter = 1
    for cat, items in categories.items():
        for name, price, cost, weight in items:
            p_id = f"PROD-{p_counter:03d}"
            products.append((p_id, cat, name, price, cost, weight, random.randint(50, 500)))
            p_counter += 1
    
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)", products)

    # Seed Orders, Items, and Deliveries
    carriers = ["ExpressAir", "SpeedyLogistics", "ApexGround", "MetroFast"]
    carrier_delay_bias = {"ExpressAir": 0.08, "SpeedyLogistics": 0.14, "ApexGround": 0.28, "MetroFast": 0.11}

    orders = []
    order_items = []
    deliveries = []

    start_date = datetime(2025, 6, 1)
    
    for o_idx in range(1, num_orders + 1):
        order_id = f"ORD-{o_idx:05d}"
        cust = random.choice(customers)
        cust_id = cust[0]

        order_dt = start_date + timedelta(days=random.randint(0, 300), hours=random.randint(8, 20))
        est_days = random.randint(2, 6)
        est_delivery_dt = order_dt + timedelta(days=est_days)

        carrier = random.choice(carriers)
        delay_prob = carrier_delay_bias[carrier]
        is_delayed = random.random() < delay_prob
        delay_days = random.randint(1, 5) if is_delayed else 0

        transit_days = est_days + delay_days
        delivered_dt = order_dt + timedelta(days=transit_days)

        # Rating: delayed orders get lower ratings
        if is_delayed:
            rating = random.choices([1, 2, 3, 4], weights=[0.45, 0.30, 0.18, 0.07])[0]
        else:
            rating = random.choices([3, 4, 5], weights=[0.05, 0.35, 0.60])[0]

        # Items in this order
        num_items = random.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05])[0]
        chosen_prods = random.sample(products, num_items)
        order_total = 0.0

        for prod in chosen_prods:
            qty = random.randint(1, 3)
            unit_p = prod[3]
            sub = round(qty * unit_p, 2)
            order_total += sub
            order_items.append((order_id, prod[0], qty, unit_p, sub))

        freight = round(12.50 + (random.random() * 25.0), 2)
        status = "Delivered" if random.random() > 0.04 else "Shipped"
        
        orders.append((order_id, cust_id, status, order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                       delivered_dt.strftime("%Y-%m-%d %H:%M:%S") if status == "Delivered" else None,
                       est_delivery_dt.strftime("%Y-%m-%d %H:%M:%S"),
                       round(order_total, 2), freight))

        deliveries.append((f"DEL-{o_idx:05d}", order_id, carrier, status, transit_days,
                           1 if is_delayed else 0, delay_days, rating))

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)", orders)
    cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)", order_items)
    cursor.executemany("INSERT INTO deliveries VALUES (?, ?, ?, ?, ?, ?, ?, ?)", deliveries)

    conn.commit()
    conn.close()
    print(f"Database successfully generated at {db_path} with {num_orders} orders!")

if __name__ == "__main__":
    generate_database()
