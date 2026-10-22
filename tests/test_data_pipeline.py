"""
test_data_pipeline.py
---------------------
Automated test suite verifying data integrity, schema expectations,
temporal logic, and referential constraints across raw and cleaned layers.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import hashlib
import sqlite3
import pytest
import pandas as pd
import numpy as np

RAW_CSV = os.path.join("data", "raw", "DataCoSupplyChainDataset.csv")
CLEAN_PARQUET = os.path.join("data", "processed", "clean_shipments.parquet")
CUSTOMS_PARQUET = os.path.join("data", "processed", "customs_trade_extension.parquet")
DB_PATH = os.path.join("data", "supply_chain_analytics.db")

EXPECTED_SHA256 = "fa6d022ed437155e1a2f0378710602848703c8a7f203f7ff5d77805bf8480aa6"
TOTAL_RECORDS = 180519
TOTAL_ORDERS = 65752

def test_raw_file_integrity():
    """Verify raw DataCo file exists and has unaltered cryptographic SHA256 hash."""
    assert os.path.exists(RAW_CSV), f"Raw dataset missing at {RAW_CSV}"
    hasher = hashlib.sha256()
    with open(RAW_CSV, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    assert hasher.hexdigest() == EXPECTED_SHA256, "Raw CSV has been altered from Mendeley original!"

def test_clean_row_count_and_granularity():
    """Verify clean dataset row count reconciles exactly to 180,519 rows with unique primary key."""
    assert os.path.exists(CLEAN_PARQUET), f"Clean parquet missing at {CLEAN_PARQUET}"
    df = pd.read_parquet(CLEAN_PARQUET)
    assert len(df) == TOTAL_RECORDS, f"Row count mismatch: expected {TOTAL_RECORDS}, got {len(df)}"
    assert df["order_item_id"].nunique() == TOTAL_RECORDS, "order_item_id is not globally unique!"
    assert df["order_id"].nunique() == TOTAL_ORDERS, f"Unique order count mismatch: {df['order_id'].nunique()}"

def test_temporal_and_duration_validity():
    """Verify temporal sequence and non-negative logistics lead times."""
    df = pd.read_parquet(CLEAN_PARQUET)
    # Temporal order
    assert (df["shipping_date"] < df["order_date"]).sum() == 0, "Found inverted dates where shipping < order!"
    # Non-negative durations
    assert (df["days_shipping_real"] < 0).sum() == 0, "Found negative real shipping days!"
    assert (df["days_shipping_scheduled"] < 0).sum() == 0, "Found negative scheduled shipping days!"

def test_financial_ranges():
    """Verify prices and sales are non-negative."""
    df = pd.read_parquet(CLEAN_PARQUET)
    assert (df["sales_gross"] <= 0).sum() == 0, "Found zero or negative gross sales!"
    assert (df["product_price"] <= 0).sum() == 0, "Found zero or negative product prices!"

def test_partition_completeness():
    """Verify mutually exclusive partition of is_late, is_on_time, and is_canceled."""
    df = pd.read_parquet(CLEAN_PARQUET)
    partition_sum = df["is_late"].sum() + df["is_on_time"].sum() + df["is_canceled"].sum()
    assert partition_sum == TOTAL_RECORDS, "Partition completeness failed: sum of statuses != total rows!"

def test_sqlite_referential_integrity():
    """Verify foreign key integrity and table counts in SQLite database."""
    assert os.path.exists(DB_PATH), f"Database missing at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    assert len(fk_violations) == 0, f"Foreign key violations found: {fk_violations}"
    
    cursor.execute("SELECT COUNT(*) FROM fact_shipments;")
    fact_count = cursor.fetchone()[0]
    assert fact_count == TOTAL_RECORDS, f"Fact table count mismatch: {fact_count} vs {TOTAL_RECORDS}"
    conn.close()

def test_synthetic_customs_lineage():
    """Verify Phase 2 synthetic customs extension integrity and lineage conventions."""
    assert os.path.exists(CUSTOMS_PARQUET), f"Customs parquet missing at {CUSTOMS_PARQUET}"
    ext_df = pd.read_parquet(CUSTOMS_PARQUET)
    assert len(ext_df) == TOTAL_ORDERS, f"Customs count should equal total orders ({TOTAL_ORDERS}), got {len(ext_df)}"
    assert ext_df["order_id"].nunique() == TOTAL_ORDERS, "order_id in customs extension is not 1-to-1 unique!"
    
    # Check that all generated columns carry 'sim_' prefix (except foreign key order_id)
    non_sim_cols = [c for c in ext_df.columns if not c.startswith("sim_") and c != "order_id"]
    assert len(non_sim_cols) == 0, f"Found synthetic columns without 'sim_' prefix: {non_sim_cols}"
    
    # Check dwell time is positive
    assert (ext_df["sim_dwell_time_days"] <= 0).sum() == 0, "Found non-positive customs dwell times!"
