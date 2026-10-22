import os
import pandas as pd
import numpy as np

def profile_raw_data(filepath: str = os.path.join("data", "raw", "DataCoSupplyChainDataset.csv")):
    print(f"Loading raw dataset from {filepath}...")
    # Read with latin-1 or utf-8 (latin-1 is standard for this dataset due to accents in customer names)
    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding="latin-1")
        encoding = "latin-1"

    print(f"Successfully loaded dataset with encoding '{encoding}'.")
    row_count, col_count = df.shape
    print(f"Total Rows: {row_count:,}")
    print(f"Total Columns: {col_count}")

    # Inspect Columns & Data Types
    col_summary = []
    for col in df.columns:
        n_missing = df[col].isna().sum()
        pct_missing = (n_missing / row_count) * 100
        n_unique = df[col].nunique(dropna=True)
        sample_val = str(df[col].dropna().iloc[0]) if n_unique > 0 else "N/A"
        col_summary.append({
            "Column": col,
            "Dtype": str(df[col].dtype),
            "Missing": n_missing,
            "Pct_Missing": round(pct_missing, 2),
            "Unique_Values": n_unique,
            "Sample": sample_val[:30]
        })

    summary_df = pd.DataFrame(col_summary)

    # Key Granularity & ID Checks
    order_id_unique = df["Order Id"].nunique()
    order_item_id_unique = df["Order Item Id"].nunique()
    full_duplicates = df.duplicated().sum()

    print("\n--- GRANULARITY & KEY INTEGRITY ---")
    print(f"Unique Order Item IDs: {order_item_id_unique:,} (Matches total rows: {order_item_id_unique == row_count})")
    print(f"Unique Order IDs: {order_id_unique:,} (Average items per order: {row_count / order_id_unique:.2f})")
    print(f"Full Duplicate Rows: {full_duplicates:,}")

    # Key Delivery & Shipping Integrity Checks
    print("\n--- DELIVERY & SHIPPING CHECKS ---")
    real_days = df["Days for shipping (real)"]
    sched_days = df["Days for shipment (scheduled)"]
    print(f"Days for shipping (real) range: [{real_days.min()}, {real_days.max()}], Mean: {real_days.mean():.2f}")
    print(f"Days for shipment (scheduled) range: [{sched_days.min()}, {sched_days.max()}], Mean: {sched_days.mean():.2f}")
    
    negative_shipping_days = (real_days < 0).sum()
    negative_sched_days = (sched_days < 0).sum()
    print(f"Negative Real Shipping Days: {negative_shipping_days}")
    print(f"Negative Scheduled Shipping Days: {negative_sched_days}")

    # Delivery Status vs Late Delivery Risk Consistency
    print("\n--- DELIVERY STATUS DISTRIBUTION ---")
    print(df["Delivery Status"].value_counts(dropna=False))
    print("\n--- LATE DELIVERY RISK DISTRIBUTION ---")
    print(df["Late_delivery_risk"].value_counts(dropna=False))

    # Cross-tab of Status vs Risk Flag
    crosstab_risk = pd.crosstab(df["Delivery Status"], df["Late_delivery_risk"])
    print("\n--- STATUS vs LATE DELIVERY RISK CROSSTAB ---")
    print(crosstab_risk)

    # Missing values highlight
    missing_cols = summary_df[summary_df["Missing"] > 0]
    print("\n--- COLUMNS WITH MISSING VALUES ---")
    print(missing_cols[["Column", "Missing", "Pct_Missing", "Dtype"]])

    # Save summary report to docs
    os.makedirs("docs", exist_ok=True)
    report_path = os.path.join("docs", "raw_dataset_profile.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Raw Dataset Profile: DataCo Smart Supply Chain\n\n")
        f.write(f"- **Source File:** `data/raw/DataCoSupplyChainDataset.csv`\n")
        f.write(f"- **Encoding:** `{encoding}`\n")
        f.write(f"- **Total Rows:** {row_count:,}\n")
        f.write(f"- **Total Columns:** {col_count}\n")
        f.write(f"- **Unique Order Items (Primary Grain):** {order_item_id_unique:,}\n")
        f.write(f"- **Unique Orders:** {order_id_unique:,}\n")
        f.write(f"- **Full Row Duplicates:** {full_duplicates}\n\n")
        
        f.write("## Delivery & Shipping Sanity Checks\n")
        f.write(f"- `Days for shipping (real)` Range: `{real_days.min()}` to `{real_days.max()}` days (Mean: {real_days.mean():.2f})\n")
        f.write(f"- `Days for shipment (scheduled)` Range: `{sched_days.min()}` to `{sched_days.max()}` days (Mean: {sched_days.mean():.2f})\n")
        f.write(f"- Negative Real Shipping Days: `{negative_shipping_days}`\n")
        f.write(f"- Negative Scheduled Shipping Days: `{negative_sched_days}`\n\n")

        f.write("## Missing Values Summary\n\n")
        f.write(missing_cols.to_markdown(index=False))
        f.write("\n\n## Full Column Schema & Profiling\n\n")
        f.write(summary_df.to_markdown(index=False))
        f.write("\n")

    print(f"\nProfiling report saved to {report_path}")
    return summary_df

if __name__ == "__main__":
    profile_raw_data()
