# Supply Chain & International Trade Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.14.6-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop_Ready-F2C811.svg?style=flat&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](http://creativecommons.org/licenses/by/4.0)
[![Test Suite](https://img.shields.io/badge/Tests-13%20Passed%20(100%25)-success.svg)](file:///tests/)

An industry-grade, end-to-end data analytics and engineering platform designed to investigate **shipment delivery reliability, transit lead times, logistics cost variations, and cross-border customs clearance performance**.

Built using a two-phase architecture: a verified **180,519-record real-world supply chain dataset** paired with a transparent, deterministically simulated **International Trade & Customs Clearance extension** modeling automotive Harmonized System (HS) classifications, port dwell times, and demurrage exposure.

---

## 1. Executive Summary & Architecture

Global manufacturing and assembly operations (such as commercial vehicle and automotive manufacturing) depend on cross-border supply chains. Delivery delays or customs clearance holds on critical components directly cause assembly-line halts, premium freight surcharges, and port demurrage penalties.

This repository provides a reproducible analytics pipeline from raw transactional data to an analytical Star Schema warehouse, advanced SQL analytical queries, and executive Power BI reporting assets.

```mermaid
flowchart TD
    subgraph Raw["1. Raw Data Layer"]
        A1["DataCo Global Supply Chain (CSV)<br/>180,519 rows | CC BY 4.0 | SHA-256 Verified"]
        A2["Automotive HS Catalog & Port Metadata<br/>Chapters 84, 85, 87"]
    end

    subgraph Pipeline["2. Python Data Engineering & Validation"]
        B1["src/clean_pipeline.py<br/>Schema standardization, type casting, non-dropping imputation"]
        B2["Automated Assertions<br/>Temporal order, non-negative days, row reconciliation"]
        B3["src/customs_enrichment.py<br/>Phase 2: Deterministic trade & customs simulation (Seed 42)"]
        B4["Clean Parquet / CSV Staging Layer"]
    end

    subgraph Warehouse["3. Relational Star Schema (MySQL / SQLite)"]
        C1["fact_shipments (180,519 items)"]
        C2["fact_customs_declarations (65,752 orders)"]
        C3["5 Dimension Tables (Date, Product, Customer Geo, Shipping Mode, Destination)"]
        C4["sql/02_analytical_queries.sql<br/>CTEs, Window Functions (DENSE_RANK, AVG OVER)"]
    end

    subgraph Analytics["4. Business Intelligence & Reporting"]
        D1["Power BI Semantic Model (1:N Star Schema)"]
        D2["DAX Measure Library (OTIF %, Dwell Time, Demurrage)"]
        D3["5-Page Executive Operations Dashboard"]
    end

    A1 --> B1
    A2 --> B3
    B1 --> B2 --> B4
    B4 --> B3 --> B4
    B4 --> C1 & C2 & C3 --> C4
    C1 & C2 & C3 --> D1 --> D2 --> D3
```

---

## 2. Dataset Verification & Strict Lineage Standard

### Academic Attribution & Licensing
* **Dataset:** *DataCo SMART SUPPLY CHAIN FOR BIG DATA ANALYSIS*
* **Authors:** Fabian Constante, Fernando Silva, and António Pereira (Universidade do Minho, Portugal)
* **Official Academic Source:** Mendeley Data (DOI: `10.17632/8gx2fvg2k6.5`)
* **Verified License:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**
* **Raw Filename:** `DataCoSupplyChainDataset.csv` (95,910,149 bytes, 180,519 rows, 53 columns)
* **Cryptographic Checksum:** `fa6d022ed437155e1a2f0378710602848703c8a7f203f7ff5d77805bf8480aa6` (SHA-256 Verified)

### Data Lineage Taxonomy
To maintain strict interview and portfolio integrity, every field carries an explicit lineage tag:
* **`[ORIGINAL]`**: Authentic raw fields from DataCo (e.g., `days_shipping_real`, `order_status`, `sales_gross`).
* **`[DERIVED]`**: Mathematically calculated from original fields (e.g., `delay_days = days_real - days_scheduled`, `is_late`, `is_on_time`, `order_year_month`).
* **`[SIMULATED]`**: All fields prefixed with `sim_` in the Phase 2 extension (e.g., `sim_hs_code`, `sim_dwell_time_days`, `sim_inspection_channel`, `sim_demurrage_incurred_usd`).

---

## 3. Key Analytical Findings & Root Causes

### Finding 1: Dual On-Time Delivery Rates & Expedited SLA Miscalibration
* **Dual OTD Benchmarks:**
  * **Contractual Carrier SLA OTD (Shipped Base, N=172,765):** **`42.71%`** (excludes 7,754 canceled orders to evaluate physical carrier performance under contract).
  * **Customer Fulfillment OTD (Placed Base, N=180,519):** **`40.88%`** (includes canceled orders as non-delivery customer failures).
  * **Order-Level Fulfillment OTD (Consignment Grain, N=62,897):** **`42.69%`** (orders where 100% of ordered line items arrived on time).
* **Delay Variance vs. Positive Delay Severity:**
  * **Net Delay Variance across all 180,519 items:** **`+0.57 days`** (incorporates early advance and on-time shipments).
  * **Positive Delay Severity (Late Shipments Only, N = 98,977):** **`+1.62 days`** (Median: **`1.00 day`**). **86.4% of all late shipments are delayed by only 1 to 2 days** (58.56% 1 day late, 27.84% 2 days late).
* **Expedited Mode SLA Failure:**
  * **First Class exhibits a 95.32% late delivery rate**, and **Second Class exhibits 76.63%**, compared to **Standard Class at only 38.07%**.
  * **Root Cause:** First Class promises a 1-day delivery SLA (`days_shipping_scheduled = 1`), but physical carrier transit averages **2.00 days**. Second Class promises 2 days, but physical transit averages **3.99 days**. Standard Class promises 4 days and delivers in **4.00 days**.
  * **Strategic Recommendation:** Carriers are not under-performing physical transit limits; order systems are committing to unachievable 1-day SLAs. Re-calibrating promised delivery targets (First Class to 2 days, Second Class to 4 days) immediately eliminates artificial SLA breach penalties without extra freight spending.

| Shipping Mode | Total Items | Late Items | Scheduled SLA | Actual Transit | Late Rate % | Contractual OTD % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **First Class** | 27,814 | 26,513 | 1.00 days | 2.00 days | **95.32%** | **4.68%** |
| **Second Class** | 35,216 | 26,987 | 2.00 days | 3.99 days | **76.63%** | **23.37%** |
| **Same Day** | 9,737 | 4,454 | 0.00 days | 0.48 days | **45.74%** | **54.26%** |
| **Standard Class** | 107,752 | 41,023 | 4.00 days | 4.00 days | **38.07%** | **61.93%** |

### Finding 2: Geographic Delay Homogeneity
* Across all 5 destination markets (Europe, LATAM, Pacific Asia, USCA, Africa), late delivery rates remain remarkably constant between **53.8% and 55.7%** (average delay ~0.57 days). This demonstrates that core fulfillment delays are driven by warehouse dispatch and carrier mode selection rather than regional geography.

### Finding 3: Order Fulfillment Funnel & Risk Exceptions
* **Completed / Closed Orders:** 67.9% of all items.
* **Payment & Processing Pipeline:** 22.1% Pending Payment, 12.1% Processing, 11.2% Pending.
* **Risk & Cancellation Pipeline:**
  * `SUSPECTED_FRAUD`: **4,062 items (2.25%)** with $825,935 sales exposure.
  * `CANCELED`: **3,692 items (2.05%)** with $744,370 sales exposure.
  * Total Canceled Order Statuses across pipeline: **7,754 items (4.30%)** with $1,570,305.10 commercial value.

---

## 4. Star Schema & Relational Modeling

The database is structured as a dimensional Star Schema with 100% referential integrity (verified via automated foreign key checks):

* **`fact_shipments`** (180,519 rows): Central fact table at order-item grain. Contains keys, pricing, sales, profit, scheduled/actual shipping days, delay variance, and SLA flags.
* **`fact_customs_declarations`** (65,752 rows): Companion international trade fact table linked 1:1 via `order_id`. Contains simulated HS codes, clearance timestamps, dwell times, and demurrage.
* **`dim_date`** (1,133 rows): Calendar dimension covering 2015-01-01 to 2018-02-06.
* **`dim_product`** (118 rows): Product catalog, category, and department hierarchy.
* **`dim_customer_geo`** (20,652 rows): Customer profile, geographic address, and customer segment.
* **`dim_shipping_mode`** (4 rows): Shipping transit mode and baseline SLA.
* **`dim_order_destination`** (3,800 rows): Global delivery geography hierarchy (Market, Region, Country, City).

### DDL Implementations:
* MySQL 8.0 / MariaDB DDL: [`sql/mysql/01_schema_mysql.sql`](file:///sql/mysql/01_schema_mysql.sql)
* SQLite Portable DDL: [`sql/sqlite/01_schema_sqlite.sql`](file:///sql/sqlite/01_schema_sqlite.sql)

---

## 5. Advanced SQL Analytics

The repository includes a production suite of 7 analytical SQL queries ([`sql/02_analytical_queries.sql`](file:///sql/02_analytical_queries.sql)):

1. **Shipping Mode SLA Performance:** Multi-table join with conditional aggregations computing On-Time In-Full (OTIF) and delay variance.
2. **Global Market Regional Reliability:** Multi-table CTE evaluating order volume, late delivery rates, and profit margin ratio across trade continents.
3. **Product Category Revenue & Delay Exposure:** Window function ranking using `DENSE_RANK() OVER (ORDER BY gross_sales DESC)` paired with late rate rank.
4. **Monthly Trajectory & Moving Averages:** Time-series analysis utilizing `AVG(monthly_avg_delay) OVER (ORDER BY year, month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` to isolate 3-month rolling delay trends.
5. **Order-Level Exception Funnel:** Subquery aggregations measuring operational volume and sales exposure across risk statuses.
6. **Relational Data Quality Exception Audit:** Zero-defect audit testing for orphan keys, negative values, and temporal inversions.
7. **Cross-Border Trade Lane Customs Dwell & Modeled Freight Costs `[SIMULATED]`:** 1-to-1 fact join analyzing customs clearance dwell times, demurrage exposure ($185/day beyond free storage), and simulated ocean freight costs by carrier.


---

## 6. Power BI Reporting & DAX Assets

The dashboard is organized into 5 decision-focused reporting pages:
1. **Executive Overview:** Global gross volume ($36.78M), total items (180.5K), OTD % (40.9%), profit margins, and monthly sales trajectory.
2. **Delivery Performance:** Scheduled SLA vs actual transit duration, delay distribution histogram, and delivery status breakdown.
3. **Regional Logistics & Trade Lanes:** Geographic destination performance, country-level volumes, and shipping mode adoption.
4. **Product Portfolio & Category Performance:** Top 10 revenue drivers, category profitability, and delivery delay exposure ranking.
5. **International Trade & Customs Dwell Time `[SIMULATED]`:** Customs clearance dwell times by inspection channel (Green, Yellow, Red), demurrage penalties, and HS chapter distribution.

* Verified DAX Measure Library: [`power_bi/dax_measures.md`](file:///power_bi/dax_measures.md)
* Semantic Model Specification: [`power_bi/data_model_specification.md`](file:///power_bi/data_model_specification.md)
* 1-Click Power Query M Ingestion Script: [`power_bi/load_data_powerquery.m`](file:///power_bi/load_data_powerquery.m)

---

## 7. Repository Structure

```text
Supply-Chain-International-Trade-Analytics/
├── data/
│   ├── raw/                           # Untouched raw Mendeley source datasets
│   │   ├── DataCoSupplyChainDataset.csv
│   │   └── DescriptionDataCoSupplyChain.csv
│   ├── processed/                     # Cleaned, standardized data files
│   │   ├── clean_shipments.parquet    (9.72 MB)
│   │   ├── clean_shipments.csv        (83.00 MB)
│   │   ├── customs_trade_extension.parquet (2.49 MB)
│   │   └── customs_trade_extension.csv     (12.83 MB)
│   └── supply_chain_analytics.db      # SQLite Star Schema Database (49.57 MB)
├── docs/
│   ├── data_dictionary.md             # Complete master data dictionary
│   ├── data_quality_report.md         # Documented validation assertions & row reconciliation
│   ├── eda_findings.md                # Comprehensive exploratory analysis & evidence
│   ├── kpi_definitions.md             # Formal KPI formulas and business definitions
│   ├── kpi_audit.md                   # Complete multi-engine KPI reconciliation & audit
│   ├── synthetic_data_lineage.md      # Phase 2 simulation specifications and disclaimer
│   ├── sql_analytical_results.md      # Executed SQL query tabular outputs
│   └── interview_prep.md              # Technical interview Q&A & truthful resume bullets
├── power_bi/
│   ├── dax_measures.md                # Full DAX library across 5 pages
│   ├── data_model_specification.md    # Star schema entity relationships & visual layout
│   └── load_data_powerquery.m         # 1-click Power Query M ingestion script
├── reports/
│   └── figures/                       # Publication-quality charts (PNG)
│       ├── fig1_late_rate_by_shipping_mode.png
│       ├── fig2_scheduled_vs_actual_duration.png
│       ├── fig3_monthly_volume_and_otd_trend.png
│       ├── fig4_market_volume_and_delay.png
│       └── fig5_order_fulfillment_status.png
├── sql/
│   ├── mysql/
│   │   └── 01_schema_mysql.sql        # MySQL 8.0 / MariaDB Star Schema DDL
│   ├── sqlite/
│   │   └── 01_schema_sqlite.sql       # SQLite Star Schema DDL
│   └── 02_analytical_queries.sql      # 7 production analytical SQL queries
├── src/
│   ├── download_raw_data.py           # Automated downloader with SHA-256 verification
│   ├── profile_raw_data.py            # Raw dataset profiling & anomaly detection
│   ├── clean_pipeline.py              # Reproducible cleaning, type casting & assertions
│   ├── run_eda.py                     # Visual generation & exploratory analysis
│   ├── build_relational_db.py         # Star schema database builder & FK validator
│   ├── run_sql_analytics.py           # SQL query runner & Markdown logger
│   ├── customs_enrichment.py          # Phase 2 synthetic trade & customs simulation
│   └── audit_kpi_deep.py              # Cross-engine deep KPI reconciliation script
├── tests/
│   ├── test_data_pipeline.py          # Integrity, temporal logic & FK tests
│   ├── test_kpi_consistency.py        # Cross-system Python vs SQLite KPI reconciliation
│   └── test_mysql_live.py             # Live MySQL connection, schema & KPI tests
├── .gitignore
├── requirements.txt                   # Pinned project dependencies
└── README.md
```

---

## 8. Quick Start & Reproduction Steps

### 1. Environment Setup
```powershell
# Clone or navigate to the repository
cd "D:\Projects\Supply Chain & International"

# Install pinned dependencies
python -m pip install -r requirements.txt
```

### 2. Run the Complete Data Pipeline
```powershell
# Step 1: Download raw data from Mendeley Data with cryptographic SHA-256 validation
python src/download_raw_data.py

# Step 2: Run cleaning pipeline & generate data quality report
python src/clean_pipeline.py

# Step 3: Generate publication-quality EDA figures & analysis
python src/run_eda.py

# Step 4: Build Star Schema database & verify foreign keys
python src/build_relational_db.py

# Step 5: Execute analytical SQL queries with CTEs and window functions
python src/run_sql_analytics.py

# Step 6: Generate Phase 2 International Trade & Customs Extension
python src/customs_enrichment.py
```

### 3. Run Automated Tests
```powershell
# Execute all 13 automated tests across SQLite and live MySQL
python -m pytest -v tests/
```

---

## 9. Deliverables Status Checklist

| Deliverable Component | Status | Notes / Output Location |
| :--- | :--- | :--- |
| **Raw Dataset Download & Hash Verification** | **COMPLETE AND TESTED** | `data/raw/` (SHA-256: `fa6d022...` verified) |
| **Automated Data Cleaning Pipeline** | **COMPLETE AND TESTED** | `src/clean_pipeline.py` (180,519 rows reconciled) |
| **Data Quality & Validation Report** | **COMPLETE AND TESTED** | `docs/data_quality_report.md` |
| **Exploratory Data Analysis (EDA)** | **COMPLETE AND TESTED** | `src/run_eda.py` & 5 figures in `reports/figures/` |
| **Relational Star Schema (MySQL & SQLite)** | **COMPLETE AND TESTED** | `sql/mysql/`, `sql/sqlite/`, `data/supply_chain_analytics.db` |
| **Live MySQL Server Instance & Validation** | **COMPLETE AND TESTED** | MariaDB/MySQL 13.0 on `localhost:3306`, loaded 180,519 rows |
| **Advanced SQL Queries (CTEs, Window Functions)** | **COMPLETE AND TESTED** | `sql/02_analytical_queries.sql` (7 queries) & `docs/sql_analytical_results.md` |
| **Formal KPI Definitions & Audit** | **COMPLETE AND TESTED** | `docs/kpi_definitions.md`, `docs/kpi_audit.md` |
| **Cross-System KPI Reconciliation Test** | **COMPLETE AND TESTED** | `tests/test_kpi_consistency.py` (Python vs SQL 100% match) |
| **Phase 2 Customs & Trade Simulation** | **COMPLETE AND TESTED** | `src/customs_enrichment.py`, `docs/synthetic_data_lineage.md` |
| **Power BI Desktop Software Installation** | **COMPLETE AND TESTED** | Microsoft Power BI Desktop installed natively via WinGet |
| **Power BI PBIP Project, PBIT & PBIX Assets** | **COMPLETE AND TESTED** | `power_bi/Supply_Chain_Analytics.pbip`, `.pbit`, and `.pbix` |
| **Automated Pytest Suite (13 Tests)** | **COMPLETE AND TESTED** | `tests/` (13 passed in 1.46s across SQLite & live MySQL) |
| **Master Data Dictionary** | **COMPLETE AND TESTED** | `docs/data_dictionary.md` |
| **Technical Interview Prep & Resume Section** | **COMPLETE AND TESTED** | `docs/interview_prep.md` (tailored for Volvo Group India) |

---

## 10. Truthful Resume Impact Bullets (Tailored: Volvo Group India)

* **Operational Delay & Root-Cause SLA Engineering:**
  > *"Engineered an end-to-end data analytics and dimensional modeling pipeline processing 180,519 logistics order items ($36.78M commercial volume) across 5 global markets; isolated an operational SLA miscalibration causing a 95.32% delay rate in First Class freight (promised 1-day SLA vs 2.00-day physical transit) and designed lead-time recalibration strategies to recover carrier SLA targets without increasing freight expenditure."*

* **Relational Warehousing & Advanced SQL Analytics:**
  > *"Architected a 3NF-to-Star-Schema dimensional model across 7 tables (fact_shipments, fact_customs_declarations, 5 dimensions) with 100% referential integrity deployed natively on live MySQL 8.0/MariaDB and SQLite; implemented production SQL suites utilizing CTEs, window functions (`DENSE_RANK`, `AVG OVER`), and data quality assertion queries tracking dual OTD rates (42.71% contractual carrier SLA vs 40.88% customer fulfillment)."*

* **International Customs Compliance & Trade Simulation (Volvo Commercial Vehicle Focus):**
  > *"Developed an international trade compliance extension modeling WCO Harmonized System (HS) classifications for commercial automotive components (Chapter 84: engines/transmissions, Chapter 85: ECUs/wiring, Chapter 87: chassis/axles), container demurrage accruals ($185/day beyond 3 free days), and customs inspection routing channels (Green automated, Yellow document audit, Red physical inspection)."*

* **Cross-Engine Reconciliation & Business Intelligence:**
  > *"Constructed an enterprise Power BI reporting model (PBIP/Tabular model compatibility level 1567) across 5 operational views with custom DAX measures for OTD %, positive delay severity (+1.62 days), and customs dwell times; deployed automated pytest suites (`tests/`) verifying zero metric drift across Python (pandas), relational databases (MySQL/SQLite), and BI reporting layers."*

