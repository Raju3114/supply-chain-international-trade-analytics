"""
test_kpi_consistency.py
-----------------------
Validates that KPI calculations computed in Python match SQL database
query results identically to the decimal place.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import sqlite3
import pytest
import pandas as pd
import numpy as np

CLEAN_PARQUET = os.path.join("data", "processed", "clean_shipments.parquet")
DB_PATH = os.path.join("data", "supply_chain_analytics.db")

@pytest.fixture(scope="module")
def python_metrics():
    df = pd.read_parquet(CLEAN_PARQUET)
    total_items = len(df)
    total_orders = df["order_id"].nunique()
    late_items = df["is_late"].sum()
    on_time_items = df["is_on_time"].sum()
    canceled_items = df["is_canceled"].sum()
    shipped_items = total_items - canceled_items
    
    gross_sales = df["sales_gross"].sum()
    net_profit = df["benefit_per_order"].sum()
    
    overall_variance = df["delay_days"].mean()
    positive_delay = df[df["is_late"] == 1]["delay_days"].mean()
    
    return {
        "total_items": total_items,
        "total_orders": total_orders,
        "otd_shipped_base_pct": round(on_time_items * 100.0 / shipped_items, 2),
        "otd_total_base_pct": round(on_time_items * 100.0 / total_items, 2),
        "late_rate_shipped_base_pct": round(late_items * 100.0 / shipped_items, 2),
        "late_rate_total_base_pct": round(late_items * 100.0 / total_items, 2),
        "delay_variance_days": round(overall_variance, 2),
        "positive_delay_days": round(positive_delay, 2),
        "gross_sales_usd": round(gross_sales, 2),
        "net_profit_usd": round(net_profit, 2)
    }

@pytest.fixture(scope="module")
def sql_metrics():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        COUNT(order_item_id) AS total_items,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(is_on_time) * 100.0 / SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END), 2) AS otd_shipped_base_pct,
        ROUND(SUM(is_on_time) * 100.0 / COUNT(order_item_id), 2) AS otd_total_base_pct,
        ROUND(SUM(is_late) * 100.0 / SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END), 2) AS late_rate_shipped_base_pct,
        ROUND(SUM(is_late) * 100.0 / COUNT(order_item_id), 2) AS late_rate_total_base_pct,
        ROUND(AVG(delay_days), 2) AS delay_variance_days,
        ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days ELSE NULL END), 2) AS positive_delay_days,
        ROUND(SUM(sales_gross), 2) AS gross_sales_usd,
        ROUND(SUM(benefit_per_order), 2) AS net_profit_usd
    FROM fact_shipments;
    """
    row = pd.read_sql_query(query, conn).iloc[0].to_dict()
    conn.close()
    return row

def test_kpi_exact_cross_system_reconciliation(python_metrics, sql_metrics):
    """Assert Python and SQL metrics are identical across all core business indicators."""
    print("\nComparing Python vs SQL metrics:")
    for key in python_metrics:
        py_val = python_metrics[key]
        sql_val = sql_metrics[key]
        print(f"  - {key}: Python={py_val} | SQL={sql_val}")
        assert py_val == sql_val, f"Discrepancy in {key}: Python={py_val}, SQL={sql_val}"

def test_shipping_mode_breakdown_consistency():
    """Verify that shipping mode metrics match between pandas and SQL joins."""
    df = pd.read_parquet(CLEAN_PARQUET)
    py_mode = df.groupby("shipping_mode").agg(
        items=("order_item_id", "count"),
        late=("is_late", "sum")
    ).reset_index()
    py_mode["late_pct"] = (py_mode["late"] * 100.0 / py_mode["items"]).round(2)
    
    conn = sqlite3.connect(DB_PATH)
    sql_mode = pd.read_sql_query("""
    SELECT 
        m.shipping_mode,
        COUNT(f.order_item_id) AS items,
        SUM(f.is_late) AS late,
        ROUND(SUM(f.is_late) * 100.0 / COUNT(f.order_item_id), 2) AS late_pct
    FROM fact_shipments f
    JOIN dim_shipping_mode m ON f.shipping_mode_id = m.shipping_mode_id
    GROUP BY m.shipping_mode
    ORDER BY m.shipping_mode;
    """, conn)
    conn.close()
    
    py_mode = py_mode.sort_values("shipping_mode").reset_index(drop=True)
    sql_mode = sql_mode.sort_values("shipping_mode").reset_index(drop=True)
    
    pd.testing.assert_frame_equal(py_mode[["shipping_mode", "items", "late", "late_pct"]], 
                                  sql_mode[["shipping_mode", "items", "late", "late_pct"]])
