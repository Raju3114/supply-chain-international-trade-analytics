"""
build_relational_db.py
----------------------
Populates the relational Star Schema database (SQLite for local offline execution,
mirroring MySQL 8.0 schema) directly from clean_shipments.parquet.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = os.path.join("data", "supply_chain_analytics.db")
PARQUET_PATH = os.path.join("data", "processed", "clean_shipments.parquet")
SCHEMA_SQL_PATH = os.path.join("sql", "sqlite", "01_schema_sqlite.sql")

def build_database():
    print("================================================================")
    print("      BUILDING STAR SCHEMA RELATIONAL DATABASE (SQLITE)         ")
    print("================================================================")
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Apply DDL
    print(f"Applying schema DDL from {SCHEMA_SQL_PATH}...")
    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        ddl_script = f.read()
    cursor.executescript(ddl_script)
    print("Schema created successfully.")

    # 2. Ingest Clean Parquet
    print(f"Loading clean dataset from {PARQUET_PATH}...")
    df = pd.read_parquet(PARQUET_PATH)
    total_rows = len(df)
    print(f"Loaded {total_rows:,} records.")

    # 3. Populate dim_date
    print("Extracting and loading dim_date...")
    # Gather all unique dates from both order_date and shipping_date
    all_dates = pd.concat([df["order_date"], df["shipping_date"]]).drop_duplicates().sort_values()
    dim_date = pd.DataFrame({"full_date": all_dates.dt.date.drop_duplicates().sort_values()})
    dim_date["full_date_dt"] = pd.to_datetime(dim_date["full_date"])
    dim_date["date_key"] = dim_date["full_date_dt"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["full_date_dt"].dt.year
    dim_date["quarter"] = "Q" + dim_date["full_date_dt"].dt.quarter.astype(str)
    dim_date["month"] = dim_date["full_date_dt"].dt.month
    dim_date["month_name"] = dim_date["full_date_dt"].dt.month_name()
    dim_date["year_month"] = dim_date["full_date_dt"].dt.strftime("%Y-%m")
    dim_date["day_of_month"] = dim_date["full_date_dt"].dt.day
    dim_date["day_of_week"] = dim_date["full_date_dt"].dt.day_name()
    
    date_records = dim_date[["date_key", "full_date", "year", "quarter", "month", 
                             "month_name", "year_month", "day_of_month", "day_of_week"]].copy()
    date_records["full_date"] = date_records["full_date"].astype(str)
    date_records.to_sql("dim_date", conn, if_exists="append", index=False)
    print(f"  -> Loaded {len(date_records):,} distinct calendar dates into dim_date.")

    # 4. Populate dim_product
    print("Extracting and loading dim_product...")
    dim_product = df[["product_id", "product_name", "category_id", "category_name", 
                      "department_id", "department_name"]].drop_duplicates(subset=["product_id"])
    dim_product.to_sql("dim_product", conn, if_exists="append", index=False)
    print(f"  -> Loaded {len(dim_product):,} distinct products into dim_product.")

    # 5. Populate dim_customer_geo
    print("Extracting and loading dim_customer_geo...")
    dim_cust = df[["customer_id", "customer_fname", "customer_lname", "customer_segment",
                   "customer_city", "customer_state", "customer_country", "customer_zipcode",
                   "customer_latitude", "customer_longitude"]].drop_duplicates(subset=["customer_id"])
    dim_cust.to_sql("dim_customer_geo", conn, if_exists="append", index=False)
    print(f"  -> Loaded {len(dim_cust):,} distinct customers into dim_customer_geo.")

    # 6. Populate dim_shipping_mode
    print("Extracting and loading dim_shipping_mode...")
    modes = [
        {"shipping_mode_id": 1, "shipping_mode": "Standard Class", "standard_scheduled_days": 4},
        {"shipping_mode_id": 2, "shipping_mode": "Second Class", "standard_scheduled_days": 2},
        {"shipping_mode_id": 3, "shipping_mode": "First Class", "standard_scheduled_days": 1},
        {"shipping_mode_id": 4, "shipping_mode": "Same Day", "standard_scheduled_days": 0},
    ]
    dim_mode = pd.DataFrame(modes)
    dim_mode.to_sql("dim_shipping_mode", conn, if_exists="append", index=False)
    print(f"  -> Loaded {len(dim_mode):,} shipping modes into dim_shipping_mode.")
    mode_map = dict(zip(dim_mode["shipping_mode"], dim_mode["shipping_mode_id"]))

    # 7. Populate dim_order_destination
    print("Extracting and loading dim_order_destination...")
    dest_cols = ["order_market", "order_region", "order_country", "order_state", "order_city", "order_zipcode"]
    dim_dest = df[dest_cols].drop_duplicates().reset_index(drop=True)
    dim_dest["destination_id"] = np.arange(1, len(dim_dest) + 1)
    
    # Save to SQL
    dim_dest.to_sql("dim_order_destination", conn, if_exists="append", index=False)
    print(f"  -> Loaded {len(dim_dest):,} unique destination geographic entities into dim_order_destination.")

    # 8. Prepare and Populate fact_shipments
    print("Transforming and loading fact_shipments...")
    # Add foreign keys
    df["order_date_key"] = df["order_date"].dt.strftime("%Y%m%d").astype(int)
    df["shipping_date_key"] = df["shipping_date"].dt.strftime("%Y%m%d").astype(int)
    df["order_timestamp"] = df["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["shipping_timestamp"] = df["shipping_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["shipping_mode_id"] = df["shipping_mode"].map(mode_map)

    # Merge destination_id
    df = df.merge(dim_dest, on=dest_cols, how="left")

    fact_cols = [
        "order_item_id", "order_id", "order_date_key", "shipping_date_key",
        "order_timestamp", "shipping_timestamp", "customer_id", "product_id",
        "shipping_mode_id", "destination_id", "order_status", "delivery_status",
        "days_shipping_real", "days_shipping_scheduled", "delay_days",
        "is_late", "is_on_time", "is_canceled", "order_item_quantity",
        "product_price", "order_item_discount", "order_item_discount_rate",
        "order_item_total", "sales_gross", "order_item_profit_ratio", "benefit_per_order"
    ]
    fact_df = df[fact_cols]
    
    # Insert in batches
    fact_df.to_sql("fact_shipments", conn, if_exists="append", index=False, chunksize=10000)
    print(f"  -> Loaded {len(fact_df):,} fact records into fact_shipments.")

    # 9. Verify Foreign Key Integrity & Row Counts
    print("\nVerifying database referential integrity...")
    cursor.execute("PRAGMA foreign_key_check;")
    fk_errors = cursor.fetchall()
    assert len(fk_errors) == 0, f"Foreign key constraint violations detected: {fk_errors}"
    print("  -> [PASS] Foreign Key Check: 0 violations across all 6 tables.")

    cursor.execute("SELECT COUNT(*) FROM fact_shipments;")
    loaded_fact_count = cursor.fetchone()[0]
    assert loaded_fact_count == total_rows, f"Fact row count mismatch: {loaded_fact_count} vs {total_rows}"
    print(f"  -> [PASS] Fact Row Count Reconciliation: exactly {loaded_fact_count:,} items.")

    conn.commit()
    conn.close()
    
    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\nDatabase build complete! SQLite database saved to: {DB_PATH} ({db_size_mb:.2f} MB)")

if __name__ == "__main__":
    build_database()
