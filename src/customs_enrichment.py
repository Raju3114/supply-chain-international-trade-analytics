"""
customs_enrichment.py
---------------------
Phase 2: International Trade & Customs Clearance Extension.

Generates a modular, explicitly labeled synthetic companion dataset for cross-border
trade operations, port dwell times, customs clearance milestones, and documentation quality.

DISCLAIMER:
All fields in this extension are synthetic simulations created for portfolio demonstration
and educational analysis of customs processes (e.g. Harmonized System classifications,
inspection channels, demurrage fees). They do NOT represent real-world statutory declarations
or confidential Volvo Group records.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import numpy as np
import pandas as pd
from datetime import timedelta

# Paths
INPUT_PARQUET = os.path.join("data", "processed", "clean_shipments.parquet")
OUTPUT_CSV = os.path.join("data", "processed", "customs_trade_extension.csv")
OUTPUT_PARQUET = os.path.join("data", "processed", "customs_trade_extension.parquet")
LINEAGE_DOC = os.path.join("docs", "synthetic_data_lineage.md")

# Automotive & Industrial Reference Data for Cross-Border Simulation
HS_CATALOG = [
    {"chapter": "84", "hs_code": "8407.34", "description": "Spark-ignition engines > 1000cc", "base_tariff_rate": 0.025},
    {"chapter": "84", "hs_code": "8408.20", "description": "Diesel / semi-diesel compression engines for commercial vehicles", "base_tariff_rate": 0.035},
    {"chapter": "84", "hs_code": "8483.40", "description": "Gears, gearing, and transmission systems", "base_tariff_rate": 0.020},
    {"chapter": "85", "hs_code": "8537.10", "description": "Electronic control units (ECUs) and digital controllers", "base_tariff_rate": 0.015},
    {"chapter": "85", "hs_code": "8544.30", "description": "Wiring harnesses and cable sets for vehicles", "base_tariff_rate": 0.028},
    {"chapter": "87", "hs_code": "8708.29", "description": "Commercial truck body assemblies and cabin components", "base_tariff_rate": 0.040},
    {"chapter": "87", "hs_code": "8708.40", "description": "Gear boxes and parts thereof for commercial vehicles", "base_tariff_rate": 0.035},
    {"chapter": "87", "hs_code": "8708.70", "description": "Road wheels and structural accessories for trucks", "base_tariff_rate": 0.030},
    {"chapter": "87", "hs_code": "8708.80", "description": "Suspension shock-absorbers and damper assemblies", "base_tariff_rate": 0.025},
]

CARRIER_PARTNERS = [
    "Maersk Line", 
    "MSC Mediterranean Shipping", 
    "CMA CGM Group", 
    "Hapag-Lloyd Logistics", 
    "Ocean Network Express (ONE)"
]

CUSTOMS_BROKERS = [
    "Kuehne+Nagel Customs Logistics",
    "DHL Global Forwarding Trade Services",
    "DB Schenker Border Solutions",
    "Expeditors International Trade Compliance"
]

PORTS_OF_ENTRY = {
    "Europe": ["Port of Rotterdam", "Port of Antwerp", "Port of Hamburg"],
    "Pacific Asia": ["Port of Singapore", "Port of Busan", "Port of Shanghai"],
    "LATAM": ["Port of Santos", "Port of Cartagena", "Port of Manzanillo"],
    "Africa": ["Port of Durban", "Port of Tanger Med", "Port of Alexandria"],
    "USCA": ["Port of Los Angeles", "Port of New York & New Jersey", "Port of Savannah"]
}

def generate_customs_extension(seed: int = 42):
    print("================================================================")
    print("   GENERATING PHASE 2: INTERNATIONAL TRADE & CUSTOMS EXTENSION  ")
    print("================================================================")
    
    np.random.seed(seed)
    print(f"Random seed initialized to {seed} for 100% deterministic reproducibility.")

    print(f"Loading core clean shipments from {INPUT_PARQUET}...")
    df = pd.read_parquet(INPUT_PARQUET)
    
    # Granularity: 1 customs declaration per distinct cross-border order (order_id)
    # Group at order level to prevent cardinality duplication
    order_level = df.groupby("order_id").agg(
        order_date=("order_date", "min"),
        shipping_date=("shipping_date", "max"),
        order_market=("order_market", "first"),
        order_country=("order_country", "first"),
        order_region=("order_region", "first"),
        customer_country=("customer_country", "first"),
        total_order_value=("order_item_total", "sum"),
        items_in_order=("order_item_id", "count")
    ).reset_index()

    n_orders = len(order_level)
    print(f"Total distinct orders to evaluate for international trade: {n_orders:,}")

    # Build simulated records
    declarations = []
    
    for i, row in order_level.iterrows():
        order_id = row["order_id"]
        order_dt = row["order_date"]
        ship_dt = row["shipping_date"]
        market = row["order_market"]
        
        dec_id = f"DEC-{order_dt.year}-{order_id:08d}"
        trade_lane = f"{row['customer_country']}-to-{row['order_region'].replace(' ', '')}"
        carrier = np.random.choice(CARRIER_PARTNERS)
        broker = np.random.choice(CUSTOMS_BROKERS)
        
        # Pick port of entry based on destination market
        possible_ports = PORTS_OF_ENTRY.get(market, ["Port of Rotterdam"])
        port_of_entry = np.random.choice(possible_ports)
        
        # Pick HS Classification
        hs_item = np.random.choice(HS_CATALOG)
        hs_chapter = hs_item["chapter"]
        hs_code = hs_item["hs_code"]
        tariff_rate = hs_item["base_tariff_rate"]
        
        # Port of Entry Arrival: 1 to 4 days after shipping_date
        port_transit_days = np.random.uniform(1.0, 4.0)
        port_arrival_dt = ship_dt + timedelta(days=float(port_transit_days))
        
        # Documentation Discrepancy Flag (5.5% baseline probability)
        # Higher probability if value is large or items > 4
        doc_error_prob = 0.055 + (0.02 if row["items_in_order"] > 4 else 0.0)
        doc_discrepancy = 1 if np.random.rand() < doc_error_prob else 0
        
        # Inspection Channel:
        # Green: 80%, Yellow: 15%, Red: 5% (Red probability increases if doc_discrepancy = 1)
        if doc_discrepancy == 1:
            channel = np.random.choice(["Green", "Yellow", "Red"], p=[0.20, 0.45, 0.35])
        else:
            channel = np.random.choice(["Green", "Yellow", "Red"], p=[0.85, 0.12, 0.03])
            
        # Clearance Duration (Dwell Time in Days):
        # Green channel: mean 1.2 days (std 0.4)
        # Yellow channel (Doc review): mean 3.2 days (std 0.8)
        # Red channel (Physical inspection): mean 5.5 days (std 1.2)
        if channel == "Green":
            dwell_days = max(0.5, np.random.normal(1.2, 0.4))
        elif channel == "Yellow":
            dwell_days = max(1.5, np.random.normal(3.2, 0.8))
        else:
            dwell_days = max(2.5, np.random.normal(5.5, 1.2))
            
        clearance_release_dt = port_arrival_dt + timedelta(days=float(dwell_days))
        
        # Demurrage Exposure: Port storage fees incurred if dwell exceeds standard 3.0 free days
        free_days = 3.0
        demurrage_days = max(0.0, dwell_days - free_days)
        demurrage_fee_usd = round(demurrage_days * 185.0, 2)  # $185 per container day
        
        # Modeled customs duty amount
        duty_usd = round(row["total_order_value"] * tariff_rate, 2)
        
        declarations.append({
            "sim_declaration_id": dec_id,
            "order_id": order_id,
            "sim_trade_lane": trade_lane,
            "sim_carrier_partner": carrier,
            "sim_customs_broker": broker,
            "sim_port_of_entry": port_of_entry,
            "sim_hs_chapter": hs_chapter,
            "sim_hs_code": hs_code,
            "sim_port_arrival_timestamp": port_arrival_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "sim_customs_release_timestamp": clearance_release_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "sim_dwell_time_days": round(dwell_days, 2),
            "sim_inspection_channel": channel,
            "sim_doc_discrepancy_flag": doc_discrepancy,
            "sim_free_days_limit": free_days,
            "sim_demurrage_days": round(demurrage_days, 2),
            "sim_demurrage_incurred_usd": demurrage_fee_usd,
            "sim_duty_amount_usd": duty_usd
        })

    ext_df = pd.DataFrame(declarations)
    print(f"\nSuccessfully generated {len(ext_df):,} synthetic customs declaration records.")
    
    # Save files
    ext_df.to_parquet(OUTPUT_PARQUET, index=False, engine="pyarrow")
    ext_df.to_csv(OUTPUT_CSV, index=False)
    print(f"  -> Saved Parquet: {OUTPUT_PARQUET} ({os.path.getsize(OUTPUT_PARQUET)/(1024*1024):.2f} MB)")
    print(f"  -> Saved CSV:     {OUTPUT_CSV} ({os.path.getsize(OUTPUT_CSV)/(1024*1024):.2f} MB)")

    # Document Lineage & Statistics
    write_lineage_doc(ext_df, LINEAGE_DOC)
    
    # Also attach table to SQLite database
    attach_to_sqlite(ext_df)
    
    return ext_df

def attach_to_sqlite(ext_df):
    import sqlite3
    db_path = os.path.join("data", "supply_chain_analytics.db")
    print(f"\nAttaching fact_customs_declarations to SQLite database: {db_path}...")
    conn = sqlite3.connect(db_path)
    
    # Create table
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_customs_declarations (
        sim_declaration_id TEXT PRIMARY KEY,
        order_id INTEGER NOT NULL,
        sim_trade_lane TEXT NOT NULL,
        sim_carrier_partner TEXT NOT NULL,
        sim_customs_broker TEXT NOT NULL,
        sim_port_of_entry TEXT NOT NULL,
        sim_hs_chapter TEXT NOT NULL,
        sim_hs_code TEXT NOT NULL,
        sim_port_arrival_timestamp TEXT NOT NULL,
        sim_customs_release_timestamp TEXT NOT NULL,
        sim_dwell_time_days REAL NOT NULL,
        sim_inspection_channel TEXT NOT NULL,
        sim_doc_discrepancy_flag INTEGER NOT NULL,
        sim_free_days_limit REAL NOT NULL,
        sim_demurrage_days REAL NOT NULL,
        sim_demurrage_incurred_usd REAL NOT NULL,
        sim_duty_amount_usd REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES fact_shipments(order_id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customs_order ON fact_customs_declarations(order_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customs_carrier ON fact_customs_declarations(sim_carrier_partner);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customs_channel ON fact_customs_declarations(sim_inspection_channel);")
    
    ext_df.to_sql("fact_customs_declarations", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print("  -> fact_customs_declarations successfully created and indexed in SQLite.")

def write_lineage_doc(df, path):
    total = len(df)
    green_pct = (df["sim_inspection_channel"] == "Green").mean() * 100
    yellow_pct = (df["sim_inspection_channel"] == "Yellow").mean() * 100
    red_pct = (df["sim_inspection_channel"] == "Red").mean() * 100
    error_pct = df["sim_doc_discrepancy_flag"].mean() * 100
    demurrage_total = df["sim_demurrage_incurred_usd"].sum()
    avg_dwell = df["sim_dwell_time_days"].mean()

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Synthetic International Trade & Customs Extension: Data Lineage & Specification\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> **Transparency Disclaimer:** The records in `customs_trade_extension.csv` are deterministically simulated\n")
        f.write("> to model international trade workflows (HS classification, customs clearance channels, port dwell times, and demurrage).\n")
        f.write("> They do NOT represent proprietary customs filings or real regulatory violations of Volvo Group.\n\n")
        
        f.write("## 1. Lineage Classification Standard\n\n")
        f.write("- **`[ORIGINAL]`**: Core shipment transaction records from DataCo (180,519 order items).\n")
        f.write("- **`[DERIVED]`**: Lead-time variance, on-time indicators, date dimensions.\n")
        f.write("- **`[SIMULATED]`**: All fields prefixed with `sim_` in the companion dataset.\n\n")

        f.write("## 2. Key Generation Parameters & Seed\n")
        f.write(f"- **Random Seed:** `42` (ensures 100% reproducible generation)\n")
        f.write(f"- **Total Simulated Declarations:** `{total:,}`\n")
        f.write(f"- **Grain:** 1 Declaration per distinct order (`order_id`)\n")
        f.write(f"- **Average Customs Dwell Time:** `{avg_dwell:.2f} days`\n")
        f.write(f"- **Documentation Discrepancy Rate:** `{error_pct:.2f}%`\n")
        f.write(f"- **Total Modeled Demurrage Exposure:** `${demurrage_total:,.2f}`\n\n")

        f.write("## 3. Inspection Channel Distribution\n\n")
        f.write(f"- **Green Channel (Automated Immediate Release):** `{green_pct:.1f}%`\n")
        f.write(f"- **Yellow Channel (Documentary Review):** `{yellow_pct:.1f}%`\n")
        f.write(f"- **Red Channel (Physical Cargo Inspection):** `{red_pct:.1f}%`\n\n")

        f.write("## 4. Field Dictionary\n\n")
        f.write("| Field Name | Lineage | Data Type | Description | Source / Formula |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        f.write("| `sim_declaration_id` | SIMULATED | STRING | Unique Bill of Entry code | Deterministic sequential format |\n")
        f.write("| `order_id` | ORIGINAL FK | INTEGER | Foreign Key to `fact_shipments` | 1-to-1 match with core orders |\n")
        f.write("| `sim_trade_lane` | SIMULATED | STRING | Origin to Destination Trade Lane | Origin Country to Dest Region |\n")
        f.write("| `sim_carrier_partner` | SIMULATED | STRING | Ocean/Freight Carrier Partner | Maersk, MSC, CMA CGM, Hapag, ONE |\n")
        f.write("| `sim_customs_broker` | SIMULATED | STRING | Customs Brokerage Agent | KN, DHL, DB Schenker, Expeditors |\n")
        f.write("| `sim_port_of_entry` | SIMULATED | STRING | International Discharge Port | Modeled by destination continent |\n")
        f.write("| `sim_hs_chapter` | SIMULATED | STRING | WCO HS 2-Digit Chapter | Automotive Chapters 84, 85, 87 |\n")
        f.write("| `sim_hs_code` | SIMULATED | STRING | WCO HS 6-Digit Tariff Subheading | Automotive engine, ECU, parts codes |\n")
        f.write("| `sim_dwell_time_days` | SIMULATED | FLOAT | Clearance lead time at port | Log-normal by channel (Green=1.2d, Red=5.5d) |\n")
        f.write("| `sim_inspection_channel` | SIMULATED | STRING | Customs Routing Channel | Green, Yellow, Red |\n")
        f.write("| `sim_doc_discrepancy_flag`| SIMULATED | INTEGER | Commercial Document Discrepancy | 1 if error found, 0 otherwise |\n")
        f.write("| `sim_demurrage_incurred_usd`| SIMULATED | FLOAT | Port storage penalty | `MAX(0, dwell - 3.0) * $185/day` |\n")

    print(f"Lineage specification documented in {path}")

if __name__ == "__main__":
    generate_customs_extension()
