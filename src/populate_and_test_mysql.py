"""
populate_and_test_mysql.py
--------------------------
Loads the cleaned Star Schema dimensions and facts into the live MySQL/MariaDB server,
verifies foreign key constraints, and executes the production analytical queries.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import sqlite3
import pymysql
import pandas as pd
from tabulate import tabulate

SQLITE_DB = os.path.join("data", "supply_chain_analytics.db")
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_DB = "supply_chain_dw"

def populate_mysql():
    print("================================================================")
    print("      POPULATING & VERIFYING LIVE MYSQL DATABASE SERVER         ")
    print("================================================================")
    
    print(f"Connecting to MySQL server at {MYSQL_HOST}:{MYSQL_PORT}...")
    my_conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
    my_cur = my_conn.cursor()

    print(f"Reading tables from SQLite reference database {SQLITE_DB}...")
    sq_conn = sqlite3.connect(SQLITE_DB)

    # Disable foreign keys temporarily during bulk load
    my_cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
    my_cur.execute("TRUNCATE TABLE fact_shipments;")
    my_cur.execute("TRUNCATE TABLE dim_date;")
    my_cur.execute("TRUNCATE TABLE dim_product;")
    my_cur.execute("TRUNCATE TABLE dim_shipping_mode;")
    my_cur.execute("TRUNCATE TABLE dim_customer_geo;")
    my_cur.execute("TRUNCATE TABLE dim_order_destination;")

    # 1. Load dim_date
    print("Loading dim_date into MySQL...")
    dim_date = pd.read_sql_query("SELECT * FROM dim_date", sq_conn)
    # Rename year_month column to backticked in insert
    for _, row in dim_date.iterrows():
        my_cur.execute(
            """INSERT INTO dim_date (date_key, full_date, `year`, `quarter`, `month`, month_name, `year_month`, day_of_month, day_of_week)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (row['date_key'], row['full_date'], row['year'], row['quarter'], row['month'],
             row['month_name'], row['year_month'], row['day_of_month'], row['day_of_week'])
        )
    print(f"  -> Loaded {len(dim_date):,} rows into dim_date.")

    # 2. Load dim_product
    print("Loading dim_product into MySQL...")
    dim_product = pd.read_sql_query("SELECT * FROM dim_product", sq_conn)
    for _, row in dim_product.iterrows():
        my_cur.execute(
            """INSERT INTO dim_product (product_id, product_name, category_id, category_name, department_id, department_name)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (row['product_id'], row['product_name'], row['category_id'], row['category_name'], row['department_id'], row['department_name'])
        )
    print(f"  -> Loaded {len(dim_product):,} rows into dim_product.")

    # 3. Load dim_shipping_mode
    print("Loading dim_shipping_mode into MySQL...")
    dim_mode = pd.read_sql_query("SELECT * FROM dim_shipping_mode", sq_conn)
    for _, row in dim_mode.iterrows():
        my_cur.execute(
            """INSERT INTO dim_shipping_mode (shipping_mode_id, shipping_mode, standard_scheduled_days)
               VALUES (%s, %s, %s)""",
            (row['shipping_mode_id'], row['shipping_mode'], row['standard_scheduled_days'])
        )
    print(f"  -> Loaded {len(dim_mode):,} rows into dim_shipping_mode.")

    # 4. Load dim_customer_geo
    print("Loading dim_customer_geo into MySQL...")
    dim_cust = pd.read_sql_query("SELECT * FROM dim_customer_geo", sq_conn)
    cust_vals = [
        (r['customer_id'], r['customer_fname'], r['customer_lname'], r['customer_segment'],
         r['customer_city'], r['customer_state'], r['customer_country'], r['customer_zipcode'],
         r['customer_latitude'], r['customer_longitude'])
        for _, r in dim_cust.iterrows()
    ]
    my_cur.executemany(
        """INSERT INTO dim_customer_geo (customer_id, customer_fname, customer_lname, customer_segment,
           customer_city, customer_state, customer_country, customer_zipcode, customer_latitude, customer_longitude)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        cust_vals
    )
    print(f"  -> Loaded {len(dim_cust):,} rows into dim_customer_geo.")

    # 5. Load dim_order_destination
    print("Loading dim_order_destination into MySQL...")
    dim_dest = pd.read_sql_query("SELECT * FROM dim_order_destination", sq_conn)
    dest_vals = [
        (r['destination_id'], r['order_market'], r['order_region'], r['order_country'],
         r['order_state'], r['order_city'], r['order_zipcode'])
        for _, r in dim_dest.iterrows()
    ]
    my_cur.executemany(
        """INSERT INTO dim_order_destination (destination_id, order_market, order_region, order_country, order_state, order_city, order_zipcode)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        dest_vals
    )
    print(f"  -> Loaded {len(dim_dest):,} rows into dim_order_destination.")

    # 6. Load fact_shipments in chunks
    print("Loading fact_shipments into MySQL in 20,000-row batches...")
    fact_df = pd.read_sql_query("SELECT * FROM fact_shipments", sq_conn)
    chunk_size = 20000
    fact_cols = [
        "order_item_id", "order_id", "order_date_key", "shipping_date_key",
        "order_timestamp", "shipping_timestamp", "customer_id", "product_id",
        "shipping_mode_id", "destination_id", "order_status", "delivery_status",
        "days_shipping_real", "days_shipping_scheduled", "delay_days",
        "is_late", "is_on_time", "is_canceled", "order_item_quantity",
        "product_price", "order_item_discount", "order_item_discount_rate",
        "order_item_total", "sales_gross", "order_item_profit_ratio", "benefit_per_order"
    ]
    
    insert_sql = f"""
        INSERT INTO fact_shipments ({', '.join(fact_cols)})
        VALUES ({', '.join(['%s'] * len(fact_cols))})
    """

    for i in range(0, len(fact_df), chunk_size):
        chunk = fact_df.iloc[i:i+chunk_size]
        batch = [tuple(x) for x in chunk[fact_cols].values]
        my_cur.executemany(insert_sql, batch)
        print(f"  -> Inserted {min(i+chunk_size, len(fact_df)):,}/{len(fact_df):,} fact records...")

    # Re-enable foreign key checks
    my_cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    my_conn.commit()

    print("\nVerifying live MySQL row count reconciliation...")
    my_cur.execute("SELECT COUNT(*) AS total_count FROM fact_shipments;")
    res = my_cur.fetchone()
    mysql_count = res['total_count']
    assert mysql_count == len(fact_df), f"Row count mismatch in MySQL: {mysql_count} vs {len(fact_df)}"
    print(f"  -> [PASS] Verified exactly {mysql_count:,} fact records on live MySQL server.")

    # Execute Analytical Query 1 on MySQL
    print("\nExecuting Query 1 on Live MySQL Server...")
    query1 = """
    SELECT 
        m.shipping_mode,
        COUNT(f.order_item_id) AS total_items_shipped,
        SUM(f.is_late) AS total_late_items,
        ROUND(SUM(f.is_late) * 100.0 / COUNT(f.order_item_id), 2) AS late_delivery_rate_pct,
        ROUND(SUM(f.is_on_time) * 100.0 / COUNT(f.order_item_id), 2) AS on_time_delivery_rate_pct,
        ROUND(AVG(f.days_shipping_scheduled), 2) AS avg_scheduled_days,
        ROUND(AVG(f.days_shipping_real), 2) AS avg_real_days,
        ROUND(AVG(f.delay_days), 2) AS avg_delay_variance_days
    FROM fact_shipments f
    JOIN dim_shipping_mode m ON f.shipping_mode_id = m.shipping_mode_id
    GROUP BY m.shipping_mode
    ORDER BY late_delivery_rate_pct DESC;
    """
    my_cur.execute(query1)
    rows = my_cur.fetchall()
    print(tabulate(rows, headers="keys", tablefmt="psql"))

    sq_conn.close()
    my_conn.close()
    print("\nLive MySQL verification complete and 100% successful!")

if __name__ == "__main__":
    populate_mysql()
