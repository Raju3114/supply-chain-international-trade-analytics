"""
clean_pipeline.py
-----------------
Reproducible data cleaning, type casting, feature engineering, and validation pipeline
for the DataCo Global Supply Chain dataset.

Author: Antigravity & Senior Data Analyst Mentor
License: MIT (Pipeline Code) / CC BY 4.0 (DataCo Source Data)
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Path Configuration
RAW_DATA_PATH = os.path.join("data", "raw", "DataCoSupplyChainDataset.csv")
PROCESSED_DIR = os.path.join("data", "processed")
PROCESSED_PARQUET_PATH = os.path.join(PROCESSED_DIR, "clean_shipments.parquet")
PROCESSED_CSV_PATH = os.path.join(PROCESSED_DIR, "clean_shipments.csv")
QUALITY_REPORT_PATH = os.path.join("docs", "data_quality_report.md")

# Strict Column Mapping: Raw -> Standardized Snake Case
COLUMN_MAPPING = {
    # Timestamps & Logistics [ORIGINAL]
    "order date (DateOrders)": "order_date",
    "shipping date (DateOrders)": "shipping_date",
    "Days for shipping (real)": "days_shipping_real",
    "Days for shipment (scheduled)": "days_shipping_scheduled",
    "Delivery Status": "delivery_status",
    "Late_delivery_risk": "late_delivery_risk",
    "Shipping Mode": "shipping_mode",
    "Type": "transaction_type",
    
    # Order Identifiers & Status [ORIGINAL]
    "Order Item Id": "order_item_id",
    "Order Id": "order_id",
    "Order Status": "order_status",
    "Order Customer Id": "order_customer_id",
    "Order Item Cardprod Id": "order_item_cardprod_id",
    
    # Financial & Commercial Fields [ORIGINAL]
    "Order Item Quantity": "order_item_quantity",
    "Order Item Product Price": "product_price",
    "Order Item Discount": "order_item_discount",
    "Order Item Discount Rate": "order_item_discount_rate",
    "Order Item Total": "order_item_total",
    "Sales": "sales_gross",
    "Order Item Profit Ratio": "order_item_profit_ratio",
    "Benefit per order": "benefit_per_order",
    "Order Profit Per Order": "order_profit_per_order",
    "Sales per customer": "sales_per_customer",
    
    # Geographic & Market Dimensions [ORIGINAL]
    "Market": "order_market",
    "Order Region": "order_region",
    "Order Country": "order_country",
    "Order State": "order_state",
    "Order City": "order_city",
    "Order Zipcode": "order_zipcode",
    
    # Customer Dimensions [ORIGINAL]
    "Customer Id": "customer_id",
    "Customer Fname": "customer_fname",
    "Customer Lname": "customer_lname",
    "Customer Segment": "customer_segment",
    "Customer Country": "customer_country",
    "Customer State": "customer_state",
    "Customer City": "customer_city",
    "Customer Street": "customer_street",
    "Customer Zipcode": "customer_zipcode",
    "Latitude": "customer_latitude",
    "Longitude": "customer_longitude",
    
    # Product & Catalog Dimensions [ORIGINAL]
    "Product Card Id": "product_id",
    "Product Name": "product_name",
    "Category Id": "category_id",
    "Category Name": "category_name",
    "Department Id": "department_id",
    "Department Name": "department_name",
    "Product Status": "product_status",
    
    # Blank / Deprecated fields to drop
    "Product Description": "DROP_product_description",
    "Product Image": "DROP_product_image",
    "Customer Email": "DROP_customer_email",
    "Customer Password": "DROP_customer_password",
}

def run_pipeline():
    start_time = datetime.now()
    print("================================================================")
    print("  SUPPLY CHAIN & LOGISTICS ANALYTICS: DATA CLEANING PIPELINE    ")
    print("================================================================")

    # 1. Ingestion
    print(f"\n[1/6] Ingesting raw dataset: {RAW_DATA_PATH}")
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw dataset not found at {RAW_DATA_PATH}. Run download script first.")

    raw_df = pd.read_csv(RAW_DATA_PATH, encoding="latin-1", low_memory=False)
    initial_rows, initial_cols = raw_df.shape
    print(f"      Ingested {initial_rows:,} rows and {initial_cols} columns.")

    # 2. Schema Standardization & Dropping Non-Analytical / 100% Empty Columns
    print("\n[2/6] Standardizing schema and filtering columns...")
    cols_to_drop = [c for c, mapped in COLUMN_MAPPING.items() if mapped.startswith("DROP_")]
    cols_to_keep = [c for c, mapped in COLUMN_MAPPING.items() if not mapped.startswith("DROP_")]
    
    df = raw_df[cols_to_keep].copy()
    rename_dict = {c: mapped for c, mapped in COLUMN_MAPPING.items() if not mapped.startswith("DROP_")}
    df.rename(columns=rename_dict, inplace=True)
    print(f"      Retained {len(df.columns)} analytical columns (Dropped {len(cols_to_drop)} empty/sensitive columns: {cols_to_drop})")

    # 3. Missing Value Imputation (Preserving 100% of rows without silent drops)
    print("\n[3/6] Handling missing values according to documented policy...")
    # Customer Lname missing: 8 rows
    df["customer_lname"] = df["customer_lname"].fillna("Unknown").astype(str).str.strip()
    df["customer_fname"] = df["customer_fname"].fillna("Unknown").astype(str).str.strip()
    
    # Customer Zipcode missing: 3 rows
    df["customer_zipcode"] = df["customer_zipcode"].fillna(-1).astype(int).astype(str).replace("-1", "UNKNOWN")
    
    # Order Zipcode missing: 86.2%
    df["order_zipcode"] = df["order_zipcode"].fillna(-1).astype(int).astype(str).replace("-1", "UNKNOWN")

    # Strip whitespace from text fields
    text_cols = ["delivery_status", "shipping_mode", "order_status", "order_market", "order_region", 
                 "order_country", "order_state", "order_city", "customer_segment", "customer_country",
                 "customer_state", "customer_city", "product_name", "category_name", "department_name"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # 4. Type Casting & Date Conversion
    print("\n[4/6] Casting types and parsing timestamps...")
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y %H:%M")
    df["shipping_date"] = pd.to_datetime(df["shipping_date"], format="%m/%d/%Y %H:%M")
    
    int_cols = ["days_shipping_real", "days_shipping_scheduled", "late_delivery_risk", 
                "order_item_id", "order_id", "order_customer_id", "customer_id", 
                "product_id", "category_id", "department_id", "order_item_quantity"]
    for col in int_cols:
        df[col] = df[col].astype(int)

    float_cols = ["product_price", "order_item_discount", "order_item_discount_rate",
                  "order_item_total", "sales_gross", "order_item_profit_ratio",
                  "benefit_per_order", "order_profit_per_order", "sales_per_customer"]
    for col in float_cols:
        df[col] = df[col].astype(float)

    # 5. Feature Engineering: Domain Derived Fields [DERIVED]
    print("\n[5/6] Engineering derived logistics & delivery metrics...")
    
    # Delivery delay in days: real - scheduled
    # Positive = delay, 0 = on-time, Negative = ahead of schedule
    df["delay_days"] = (df["days_shipping_real"] - df["days_shipping_scheduled"]).astype(int)
    
    # Is Late Flag:
    # 1 if delivery_status is 'Late delivery' (or delay_days > 0 for completed shipments), 0 otherwise
    df["is_late"] = (df["delivery_status"] == "Late delivery").astype(int)
    
    # Canceled flag
    df["is_canceled"] = (df["delivery_status"] == "Shipping canceled").astype(int)
    
    # On-Time Delivery Flag:
    # 1 if delivered on or before scheduled deadline (Advance shipping or Shipping on time)
    df["is_on_time"] = df["delivery_status"].isin(["Shipping on time", "Advance shipping"]).astype(int)
    
    # Lead time calendar days from timestamps
    df["calendar_days_to_ship"] = (df["shipping_date"] - df["order_date"]).dt.total_seconds() / 86400.0

    # Date hierarchy for analytics & Power BI
    df["order_year"] = df["order_date"].dt.year
    df["order_month_num"] = df["order_date"].dt.month
    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["order_quarter"] = "Q" + df["order_date"].dt.quarter.astype(str)
    df["order_day_of_week"] = df["order_date"].dt.day_name()

    # 6. Automated Assertions & Validation Checks
    print("\n[6/6] Executing automated data quality assertions...")
    final_rows, final_cols = df.shape
    
    # Row Count Reconciliation
    assert initial_rows == final_rows, f"Row count mismatch! Ingested: {initial_rows}, Final: {final_rows}"
    print(f"      [PASS] Row count reconciliation: exactly {final_rows:,} rows preserved.")

    # Unique Granularity Check
    assert df["order_item_id"].nunique() == final_rows, "Primary key check failed: order_item_id is not unique!"
    print(f"      [PASS] Granularity assertion: order_item_id is unique across all {final_rows:,} rows.")

    # Timestamp Order Check: shipping_date >= order_date
    date_inversions = (df["shipping_date"] < df["order_date"]).sum()
    assert date_inversions == 0, f"Found {date_inversions} records where shipping_date < order_date!"
    print("      [PASS] Temporal consistency: shipping_date >= order_date across 100% of rows.")

    # Non-negative durations
    assert (df["days_shipping_real"] < 0).sum() == 0, "Found negative real shipping days!"
    assert (df["days_shipping_scheduled"] < 0).sum() == 0, "Found negative scheduled shipping days!"
    print("      [PASS] Non-negativity assertion: all shipping days are >= 0.")

    # Financial validity
    assert (df["sales_gross"] < 0).sum() == 0, "Found negative gross sales!"
    assert (df["product_price"] < 0).sum() == 0, "Found negative product prices!"
    print("      [PASS] Financial assertions: prices and gross sales are non-negative.")

    # Status consistency for non-canceled shipments:
    non_canceled = df[df["is_canceled"] == 0]
    late_status_match = ((non_canceled["delivery_status"] == "Late delivery") == (non_canceled["delay_days"] > 0)).all()
    assert late_status_match, "Discrepancy between 'delivery_status == Late delivery' and 'delay_days > 0' in non-canceled shipments!"
    print(f"      [PASS] Status consistency: for all {len(non_canceled):,} non-canceled shipments, 'Late delivery' matches delay_days > 0 100%.")

    # Complete mutually exclusive partition check
    partition_sum = df["is_late"].sum() + df["is_on_time"].sum() + df["is_canceled"].sum()
    assert partition_sum == final_rows, f"Partition error: sum of late ({df['is_late'].sum()}), on-time ({df['is_on_time'].sum()}), and canceled ({df['is_canceled'].sum()}) != total {final_rows}!"
    print(f"      [PASS] Partition completeness: Late ({df['is_late'].sum():,}) + On-Time ({df['is_on_time'].sum():,}) + Canceled ({df['is_canceled'].sum():,}) = {final_rows:,} items.")

    # Save Cleaned Data
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"\nSaving clean datasets to {PROCESSED_DIR}...")
    df.to_parquet(PROCESSED_PARQUET_PATH, index=False, engine="pyarrow")
    print(f"  -> Saved Parquet: {PROCESSED_PARQUET_PATH} ({os.path.getsize(PROCESSED_PARQUET_PATH) / (1024*1024):.2f} MB)")
    
    # Also save CSV for easy database import & Power BI import
    df.to_csv(PROCESSED_CSV_PATH, index=False)
    print(f"  -> Saved CSV:     {PROCESSED_CSV_PATH} ({os.path.getsize(PROCESSED_CSV_PATH) / (1024*1024):.2f} MB)")

    # Generate Data Quality Report
    generate_data_quality_report(initial_rows, final_rows, df, QUALITY_REPORT_PATH)
    
    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nPipeline successfully completed in {duration:.2f} seconds!")
    return df

def generate_data_quality_report(initial_rows, final_rows, df, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Data Quality & Validation Report\n\n")
        f.write("## 1. Executive Summary\n")
        f.write(f"- **Execution Timestamp:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n")
        f.write(f"- **Input Records:** `{initial_rows:,}`\n")
        f.write(f"- **Output Records:** `{final_rows:,}`\n")
        f.write(f"- **Row Retention Rate:** `100.0%` (Zero silent record drops)\n")
        f.write(f"- **Primary Grain:** Unique `order_item_id` (1 row = 1 ordered product item)\n")
        f.write(f"- **Distinct Orders:** `{df['order_id'].nunique():,}`\n")
        f.write(f"- **Distinct Customers:** `{df['customer_id'].nunique():,}`\n")
        f.write(f"- **Distinct Products:** `{df['product_id'].nunique():,}` across `{df['category_name'].nunique()}` categories\n\n")

        f.write("## 2. Automated Quality Assertion Outcomes\n\n")
        f.write("| Quality Check Description | Target Condition | Measured Result | Status |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| Row Count Reconciliation | Input == Output ({initial_rows:,}) | {final_rows:,} | **PASS** |\n")
        f.write(f"| Primary Key Uniqueness | `order_item_id` unique | {df['order_item_id'].nunique():,} unique | **PASS** |\n")
        f.write(f"| Temporal Sequencing | `shipping_date >= order_date` | 0 inversions | **PASS** |\n")
        f.write(f"| Non-Negative Durations | `days_shipping_real >= 0` | Min: {df['days_shipping_real'].min()} | **PASS** |\n")
        f.write(f"| Non-Negative Durations | `days_shipping_scheduled >= 0` | Min: {df['days_shipping_scheduled'].min()} | **PASS** |\n")
        f.write(f"| Financial Range Validity | `sales_gross >= 0` | Min: ${df['sales_gross'].min():.2f} | **PASS** |\n")
        f.write(f"| Financial Range Validity | `product_price >= 0` | Min: ${df['product_price'].min():.2f} | **PASS** |\n")
        f.write(f"| Late Delivery Logic Consistency | `Late delivery == (delay_days > 0)` | 100% agreement ({df['is_late'].sum():,} late) | **PASS** |\n\n")

        f.write("## 3. Missing Value Handling & Imputation Policy\n\n")
        f.write("| Field | Missing Count | Handling Method | Rationale |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write("| `Product Description` | 180,519 (100%) | Dropped column | Column was 100% blank in raw source. Product name and category provide sufficient descriptive grain. |\n")
        f.write("| `Customer Password` / `Email` | 0 | Dropped columns | PII / dummy credentials unnecessary for supply chain analytics. |\n")
        f.write("| `Customer Lname` | 8 (0.004%) | Imputed with `'Unknown'` | Negligible fraction; preserving row preserves order integrity. |\n")
        f.write("| `Customer Zipcode` | 3 (0.001%) | Imputed with `'UNKNOWN'` | Geo analysis relies primarily on City, State, Country, and Market. |\n")
        f.write("| `Order Zipcode` | 155,679 (86.2%) | Imputed with `'UNKNOWN'` | Destination analysis utilizes `order_city`, `order_state`, `order_country`, and `order_region`. |\n\n")

        f.write("## 4. Key Performance Indicators (Core Ground Truth)\n\n")
        otd_pct = (df['is_on_time'].sum() / len(df)) * 100
        late_pct = (df['is_late'].sum() / len(df)) * 100
        avg_delay = df[df['is_late'] == 1]['delay_days'].mean()
        median_delay = df[df['is_late'] == 1]['delay_days'].median()
        
        f.write(f"- **Total Order Items:** {len(df):,}\n")
        f.write(f"- **Late Deliveries:** {df['is_late'].sum():,} ({late_pct:.2f}% of all items)\n")
        f.write(f"- **On-Time Deliveries:** {df['is_on_time'].sum():,} ({otd_pct:.2f}% of all items)\n")
        f.write(f"- **Average Delay for Late Shipments:** `{avg_delay:.2f} days` (Median: `{median_delay:.1f} days`)\n")
        f.write(f"- **Total Gross Sales:** `${df['sales_gross'].sum():,.2f}`\n")
        f.write(f"- **Total Order Profit:** `${df['benefit_per_order'].sum():,.2f}`\n\n")

        f.write("## 5. Shipping Mode Breakdown\n\n")
        mode_summary = df.groupby("shipping_mode").agg(
            Items=("order_item_id", "count"),
            Late_Items=("is_late", "sum"),
            Avg_Real_Days=("days_shipping_real", "mean"),
            Avg_Sched_Days=("days_shipping_scheduled", "mean")
        ).reset_index()
        mode_summary["Late_Rate_%"] = (mode_summary["Late_Items"] / mode_summary["Items"] * 100).round(2)
        f.write(mode_summary.to_markdown(index=False))
        f.write("\n")

    print(f"Data quality report saved to {output_path}")

if __name__ == "__main__":
    run_pipeline()
