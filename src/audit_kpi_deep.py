"""
audit_kpi_deep.py
-----------------
Deep calculation of delivery performance, delay distributions,
order-level vs item-level comparisons, and synthetic customs statistics.
"""

import pandas as pd
import numpy as np

def run_deep_audit():
    df = pd.read_parquet("data/processed/clean_shipments.parquet")
    ext_df = pd.read_parquet("data/processed/customs_trade_extension.parquet")
    
    total_items = len(df)
    total_orders = df["order_id"].nunique()
    
    print("=== 1. ITEM-LEVEL DELIVERY PERFORMANCE ===")
    print(f"Total Order Items: {total_items:,}")
    
    # Status partition
    late_items = df["is_late"].sum()
    on_time_items = df["is_on_time"].sum()
    canceled_items = df["is_canceled"].sum()
    delivered_items = total_items - canceled_items
    
    print(f"Late Items: {late_items:,} ({late_items/total_items*100:.2f}% of total, {late_items/delivered_items*100:.2f}% of delivered)")
    print(f"On-Time Items: {on_time_items:,} ({on_time_items/total_items*100:.2f}% of total, {on_time_items/delivered_items*100:.2f}% of delivered)")
    print(f"Canceled Items: {canceled_items:,} ({canceled_items/total_items*100:.2f}% of total)")
    
    print("\n=== 2. DELAY VARIANCE VS POSITIVE DELAY ===")
    # Delay variance across all items
    mean_variance_all = df["delay_days"].mean()
    median_variance_all = df["delay_days"].median()
    print(f"Overall Delay Variance (All Items): Mean = {mean_variance_all:+.2f} days, Median = {median_variance_all:.1f} days")
    
    # Positive delay for late items only
    late_df = df[df["is_late"] == 1]
    mean_delay_late = late_df["delay_days"].mean()
    median_delay_late = late_df["delay_days"].median()
    print(f"Positive Delay (Late Items Only): Mean = +{mean_delay_late:.2f} days, Median = {median_delay_late:.1f} days")
    
    print("\nDelay Distribution (Late Items):")
    late_dist = late_df["delay_days"].value_counts().sort_index()
    for d, count in late_dist.items():
        print(f"  Delayed by {d} day(s): {count:,} items ({count/late_items*100:.2f}%)")
        
    print("\nDelay Distribution (All Items):")
    all_dist = df["delay_days"].value_counts().sort_index()
    for d, count in all_dist.items():
        label = "Ahead by" if d < 0 else ("On-Time (0 days)" if d == 0 else "Late by")
        print(f"  {label} {abs(d)} day(s): {count:,} items ({count/total_items*100:.2f}%)")

    print("\n=== 3. ORDER-LEVEL GRANULARITY (CONSIGNMENT LEVEL) ===")
    order_grp = df.groupby("order_id").agg(
        items_count=("order_item_id", "count"),
        any_late=("is_late", "max"),
        all_on_time=("is_on_time", "min"),
        is_canceled=("is_canceled", "max"),
        max_delay=("delay_days", "max"),
        avg_delay=("delay_days", "mean")
    ).reset_index()
    
    late_orders = (order_grp["any_late"] == 1).sum()
    ontime_orders = (order_grp["all_on_time"] == 1).sum()
    canceled_orders = (order_grp["is_canceled"] == 1).sum()
    delivered_orders = total_orders - canceled_orders
    
    print(f"Total Unique Orders: {total_orders:,}")
    print(f"Late Orders (at least 1 item late): {late_orders:,} ({late_orders/total_orders*100:.2f}% of total, {late_orders/delivered_orders*100:.2f}% of delivered)")
    print(f"On-Time Orders (100% items on time): {ontime_orders:,} ({ontime_orders/total_orders*100:.2f}% of total, {ontime_orders/delivered_orders*100:.2f}% of delivered)")
    print(f"Canceled Orders: {canceled_orders:,} ({canceled_orders/total_orders*100:.2f}% of total)")
    print(f"Mean Order-Level Delay (Late Orders): +{order_grp[order_grp['any_late']==1]['max_delay'].mean():.2f} days")

    print("\n=== 4. SHIPPING COST & FREIGHT EXPENSE REALITY CHECK ===")
    print("Does raw dataset contain actual freight expense column?")
    freight_cols = [c for c in df.columns if "freight" in c.lower() or "shipping_cost" in c.lower()]
    print(f"Freight expense columns detected in real dataset: {freight_cols} -> NONE.")
    print("Available financial columns:")
    fin_cols = ["sales_gross", "product_price", "order_item_discount", "benefit_per_order"]
    for c in fin_cols:
        print(f"  - {c}: Sum = ${df[c].sum():,.2f}, Mean = ${df[c].mean():,.2f}")

    print("\n=== 5. PHASE 2 SYNTHETIC EXTENSION VERIFICATION ===")
    print(f"Customs Declarations Count: {len(ext_df):,}")
    print(f"1-to-1 match with unique orders: {len(ext_df) == total_orders}")
    print(f"Average Customs Dwell Time: {ext_df['sim_dwell_time_days'].mean():.2f} days")
    print(f"Demurrage Incurred Total: ${ext_df['sim_demurrage_incurred_usd'].sum():,.2f}")
    print(f"Demurrage Impacted Consignments: {(ext_df['sim_demurrage_days'] > 0).sum():,} ({(ext_df['sim_demurrage_days'] > 0).mean()*100:.2f}%)")
    print(f"Doc Discrepancy Rate: {ext_df['sim_doc_discrepancy_flag'].mean()*100:.2f}%")
    print("Inspection Channels:")
    print(ext_df["sim_inspection_channel"].value_counts(normalize=True)*100)

if __name__ == "__main__":
    run_deep_audit()
