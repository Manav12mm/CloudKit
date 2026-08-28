"""Synthetic dataset seeder for Company Analytics Database."""

import random
from datetime import datetime, timedelta
import logging
from sqlalchemy import text, Engine
from database.connection import get_db_engine, get_dialect_name

logger = logging.getLogger(__name__)

def seed_database(engine: Engine = None):
    """Create tables and populate synthetic enterprise data for SQLite and MySQL."""
    engine = engine or get_db_engine()
    dialect = get_dialect_name()

    logger.info(f"Seeding database using dialect '{dialect}'...")

    # Drop all existing tables dynamically if re-seeding
    from sqlalchemy import inspect
    try:
        insp = inspect(engine)
        all_existing_tables = insp.get_table_names()
    except Exception:
        all_existing_tables = []

    with engine.begin() as conn:
        if dialect == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        elif dialect == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            
        for t in all_existing_tables:
            conn.execute(text(f"DROP TABLE IF EXISTS `{t}`;"))
            
        if dialect == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        elif dialect == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = ON;"))

    # Table creation DDL
    ddl_statements = [
        # 1. Departments
        """
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            department_name VARCHAR(100) NOT NULL,
            budget DECIMAL(12,2) NOT NULL,
            location VARCHAR(100) NOT NULL
        );
        """,
        # 2. Employees
        """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            employee_name VARCHAR(100) NOT NULL,
            department_id INTEGER NOT NULL,
            role VARCHAR(100) NOT NULL,
            salary DECIMAL(10,2) NOT NULL,
            joining_date DATE NOT NULL,
            email VARCHAR(100),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );
        """,
        # 3. Regions
        """
        CREATE TABLE regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            region_name VARCHAR(50) NOT NULL,
            country VARCHAR(50) NOT NULL
        );
        """,
        # 4. Customers
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            customer_name VARCHAR(100) NOT NULL,
            region_id INTEGER NOT NULL,
            customer_segment VARCHAR(50) NOT NULL,
            created_at DATE NOT NULL,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
        """,
        # 5. Suppliers
        """
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            supplier_name VARCHAR(100) NOT NULL,
            rating DECIMAL(3,2) NOT NULL,
            country VARCHAR(50) NOT NULL
        );
        """,
        # 6. Products
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            supplier_id INTEGER NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            cost_price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        );
        """,
        # 7. Orders
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            order_status VARCHAR(20) NOT NULL,
            shipping_cost DECIMAL(8,2) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        """,
        # 8. Order Items
        """
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            discount DECIMAL(4,2) DEFAULT 0.00,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """,
        # 9. Payments
        """
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite,
            order_id INTEGER NOT NULL,
            payment_date DATE NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        """
    ]

    with engine.begin() as conn:
        for ddl in ddl_statements:
            if dialect == "sqlite":
                clean_ddl = ddl.replace("AUTOINCREMENT if_sqlite", "AUTOINCREMENT")
            else:
                clean_ddl = ddl.replace("INTEGER PRIMARY KEY AUTOINCREMENT if_sqlite", "INT AUTO_INCREMENT PRIMARY KEY")
            conn.execute(text(clean_ddl))

    logger.info("Tables created successfully. Inserting sample data...")

    # Insert Data
    random.seed(42)

    with engine.begin() as conn:
        # Departments
        depts = [
            ("AI & Machine Learning", 1500000.00, "San Francisco"),
            ("Data Science & Analytics", 1200000.00, "New York"),
            ("Cyber Security", 1100000.00, "Washington DC"),
            ("Cloud Infrastructure", 1350000.00, "Seattle"),
            ("Software Engineering", 2000000.00, "Austin")
        ]
        for name, budget, loc in depts:
            conn.execute(text("INSERT INTO departments (department_name, budget, location) VALUES (:n, :b, :l)"),
                         {"n": name, "b": budget, "l": loc})

        # Regions
        regions = [
            ("North America", "United States"),
            ("Europe", "United Kingdom"),
            ("Asia Pacific", "Singapore"),
            ("Latin America", "Brazil")
        ]
        for r_name, country in regions:
            conn.execute(text("INSERT INTO regions (region_name, country) VALUES (:r, :c)"),
                         {"r": r_name, "c": country})

        # Suppliers
        suppliers = [
            ("NVIDIA Tech", 4.9, "USA"),
            ("TSMC Foundry", 4.8, "Taiwan"),
            ("AWS Services", 4.7, "USA"),
            ("Global Cloud Systems", 4.5, "Germany"),
            ("DataCore Solutions", 4.4, "Singapore")
        ]
        for s_name, rating, country in suppliers:
            conn.execute(text("INSERT INTO suppliers (supplier_name, rating, country) VALUES (:n, :r, :c)"),
                         {"n": s_name, "r": rating, "c": country})

        # Employees (~40 employees across departments and joining dates)
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery", "Dakota", "Reese", "Quinn", "Skyler", "Cameron"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
        roles = {
            1: ["AI Research Scientist", "ML Engineer", "LLM Specialist", "Computer Vision Engineer"],
            2: ["Data Analyst", "Senior Data Scientist", "BI Engineer", "Data Architect"],
            3: ["Security Analyst", "Penetration Tester", "SOC Manager", "Security Architect"],
            4: ["DevOps Engineer", "Cloud Architect", "Site Reliability Engineer", "System Admin"],
            5: ["Backend Developer", "Frontend Developer", "Full Stack Engineer", "Principal Engineer"]
        }

        base_date = datetime(2021, 1, 1)
        for i in range(1, 45):
            dept_id = random.randint(1, 5)
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            role = random.choice(roles[dept_id])
            # Higher salary for AI and Cloud
            base_sal = 85000 + (dept_id * 5000)
            salary = round(base_sal + random.randint(0, 70000), 2)
            joining_days = random.randint(0, 1800)
            jdate = (base_date + timedelta(days=joining_days)).strftime("%Y-%m-%d")
            email = f"{fname.lower()}.{lname.lower()}{i}@company.com"
            conn.execute(
                text("INSERT INTO employees (employee_name, department_id, role, salary, joining_date, email) VALUES (:n, :d, :r, :s, :j, :e)"),
                {"n": name, "d": dept_id, "r": role, "s": salary, "j": jdate, "e": email}
            )

        # Customers (30 customers)
        segments = ["Enterprise", "Mid-Market", "SMB"]
        for i in range(1, 31):
            cname = f"Company {chr(65 + (i % 26))}{i}"
            reg_id = random.randint(1, 4)
            seg = random.choice(segments)
            cdate = (base_date + timedelta(days=random.randint(0, 1200))).strftime("%Y-%m-%d")
            conn.execute(
                text("INSERT INTO customers (customer_name, region_id, customer_segment, created_at) VALUES (:n, :r, :s, :c)"),
                {"n": cname, "r": reg_id, "s": seg, "c": cdate}
            )

        # Products (12 products)
        prods = [
            ("H100 GPU Cluster", "Hardware", 1, 25000.00, 18000.00),
            ("A100 Tensor Node", "Hardware", 1, 12000.00, 8500.00),
            ("Wafer Slice Chipset", "Hardware", 2, 4500.00, 3000.00),
            ("Cloud Compute Instance - 64vCPU", "Cloud", 3, 1200.00, 600.00),
            ("Enterprise Kubernetes Hub", "Software", 4, 5000.00, 2000.00),
            ("AI Data Pipeline Suite", "Software", 5, 8000.00, 3500.00),
            ("Cyber Threat Monitor", "Software", 4, 3500.00, 1500.00),
            ("High-Speed Optical Interconnect", "Hardware", 2, 900.00, 500.00),
            ("Managed Vector Database", "Cloud", 3, 2200.00, 1000.00),
            ("Developer Analytics SDK", "Software", 5, 1500.00, 400.00)
        ]
        for pname, cat, supp_id, u_price, c_price in prods:
            conn.execute(
                text("INSERT INTO products (product_name, category, supplier_id, unit_price, cost_price) VALUES (:p, :c, :s, :u, :cp)"),
                {"p": pname, "c": cat, "s": supp_id, "u": u_price, "cp": c_price}
            )

        # Orders (~80 orders spanning 2024 to 2026)
        order_statuses = ["Completed", "Completed", "Completed", "Pending", "Cancelled", "Returned"]
        start_order_date = datetime(2024, 1, 1)

        for o_id in range(1, 85):
            cust_id = random.randint(1, 30)
            odays = random.randint(0, 950)
            odate = (start_order_date + timedelta(days=odays)).strftime("%Y-%m-%d")
            ostatus = random.choice(order_statuses)
            ship_cost = round(random.uniform(50.0, 500.0), 2)

            conn.execute(
                text("INSERT INTO orders (customer_id, order_date, order_status, shipping_cost) VALUES (:c, :d, :s, :sc)"),
                {"c": cust_id, "d": odate, "s": ostatus, "sc": ship_cost}
            )

            # Order Items (1 to 4 items per order)
            num_items = random.randint(1, 4)
            order_total = 0.0
            for _ in range(num_items):
                prod_id = random.randint(1, 10)
                qty = random.randint(1, 5)
                # fetch unit price
                u_price = prods[prod_id - 1][3]
                disc = random.choice([0.00, 0.05, 0.10])
                line_total = (u_price * qty) * (1 - disc)
                order_total += line_total

                conn.execute(
                    text("INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES (:oid, :pid, :q, :u, :d)"),
                    {"oid": o_id, "pid": prod_id, "q": qty, "u": u_price, "d": disc}
                )

            # Payment for completed/pending orders
            if ostatus in ["Completed", "Returned"]:
                pmethod = random.choice(["Credit Card", "Wire Transfer", "PayPal"])
                conn.execute(
                    text("INSERT INTO payments (order_id, payment_date, payment_method, amount, status) VALUES (:oid, :pd, :pm, :a, :st)"),
                    {"oid": o_id, "pd": odate, "pm": pmethod, "a": round(order_total + ship_cost, 2), "st": "Success"}
                )

    logger.info("Database seeding complete!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
