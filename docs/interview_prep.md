# Technical Interview Preparation & Resume Impact Guide

This guide prepares you to speak authoritatively about this project in technical interviews, specifically tailored for **Volvo Group India — Custom & Trade International Data Analyst** and related Global Logistics / Supply Chain Analytics engineering roles.

---

## 1. Tailored Resume Section: Volvo Group India (Custom & Trade International Data Analyst)

Copy and adapt these high-impact, ground-truth-backed bullet points into your resume experience / projects section:

### Role / Project Title:
**Supply Chain & International Trade Analytics Platform** | *Python, MySQL, SQLite, Power BI (DAX), Pytest, Git*

* **Operational Delay & Root-Cause SLA Engineering:**
  > *"Engineered an end-to-end data analytics and dimensional modeling pipeline processing 180,519 logistics order items ($36.78M commercial volume) across 5 global markets; isolated an operational SLA miscalibration causing a 95.32% delay rate in First Class freight (promised 1-day SLA vs 2.00-day physical transit) and designed lead-time recalibration strategies to recover carrier SLA targets without increasing freight expenditure."*

* **Relational Warehousing & Advanced SQL Analytics:**
  > *"Architected a 3NF-to-Star-Schema dimensional model across 7 tables (fact_shipments, fact_customs_declarations, 5 dimensions) with 100% referential integrity deployed natively on live MySQL 8.0/MariaDB and SQLite; implemented production SQL suites utilizing CTEs, window functions (`DENSE_RANK`, `AVG OVER`), and data quality assertion queries tracking dual OTD rates (42.71% contractual carrier SLA vs 40.88% customer fulfillment)."*

* **International Customs Compliance & Trade Simulation (Volvo Commercial Vehicle Focus):**
  > *"Developed an international trade compliance extension modeling WCO Harmonized System (HS) classifications for commercial automotive components (Chapter 84: engines/transmissions, Chapter 85: ECUs/wiring, Chapter 87: chassis/axles), container demurrage accruals ($185/day beyond 3 free days), and customs inspection routing channels (Green automated, Yellow document audit, Red physical inspection)."*

* **Cross-Engine Reconciliation & Business Intelligence:**
  > *"Constructed an enterprise Power BI reporting model (PBIP/Tabular model compatibility level 1567) across 5 operational views with custom DAX measures for OTD %, positive delay severity (+1.62 days), and customs dwell times; deployed automated pytest suites (`tests/`) verifying zero metric drift across Python (pandas), relational databases (MySQL/SQLite), and BI reporting layers."*

---

## 2. Technical Interview Questions & Model Answers

### Q1: "Walk me through the architecture and grain of your supply chain data pipeline."
**Model Answer:**
> *"The project follows an industry-standard dimensional modeling lifecycle from raw transactional logs to relational storage and executive business intelligence.
> 
> The pipeline starts with 180,519 raw transactional records from Mendeley Data under a CC BY 4.0 license, verified using SHA-256 (`fa6d022...`). The primary grain of the core pipeline is the **unique order item** (`order_item_id`), representing an individual SKU ordered within a customer purchase.
> 
> In the data engineering layer (`src/clean_pipeline.py`), I enforced a strict zero-silent-drop policy: missing postal codes and customer names were imputed with descriptive sentinels (`'UNKNOWN'`), and 100% of rows (180,519) were preserved. I parsed temporal timestamps, standardized column names to snake_case, and built automated quality assertions verifying chronological sequencing (`shipping_date >= order_date`) and non-negative transit days.
> 
> In the database layer, I modeled a Star Schema featuring `fact_shipments` linked to 5 dimensions (`dim_date`, `dim_product`, `dim_customer_geo`, `dim_shipping_mode`, `dim_order_destination`) and a 1:1 companion fact table `fact_customs_declarations` (65,752 distinct orders) deployed on both SQLite and a live MySQL/MariaDB server.
> 
> Finally, I established an enterprise Power BI model in PBIP/PBIX format with dedicated DAX measures reconciling delivery performance, regional trade lanes, and customs clearance dwell times."*

---

### Q2: "Why do you report two different On-Time Delivery (OTD) rates? What is the business difference?"
**Model Answer:**
> *"In enterprise supply chains—especially in cross-border automotive logistics—confusing carrier performance with overall customer fulfillment creates severe organizational friction. Therefore, I established two distinct, mathematically audited OTD metrics:
> 
> 1. **Contractual Carrier SLA OTD Rate (42.71%):**
>    - **Formula:** $\frac{\text{On-Time Shipped Items (73,788)}}{\text{Total Shipped Items (172,765)}}$
>    - **Business Meaning:** Evaluates physical freight carrier performance strictly on shipments that were actually dispatched and tendered to logistics carriers, excluding 7,754 canceled orders. This is the metric used for carrier contract negotiations, penalties, and SLA governance.
> 
> 2. **Customer Fulfillment OTD Rate (40.88%):**
>    - **Formula:** $\frac{\text{On-Time Shipped Items (73,788)}}{\text{Total Placed Items (180,519)}}$
>    - **Business Meaning:** Evaluates end-to-end customer promise fulfillment. Canceled orders (7,754 items / 4.30%) represent unfulfilled demand and failure to deliver.
> 
> Additionally, at the **consignment/order level**, where an entire order is considered on-time only if 100% of its constituent line items arrive on schedule, the on-time rate is **42.69%** (26,849 of 62,897 shipped orders). Presenting both rates shows recruiters that I understand the difference between carrier contract metrics and executive business operations."*

---

### Q3: "What is the difference between Delay Variance and Positive Delay Severity in your analysis?"
**Model Answer:**
> *"Reporting a single 'average delay' across all shipments can be deceptive because early deliveries (negative variance) cancel out late deliveries (positive variance):
> 
> - **Overall Delay Variance (+0.57 days):**
>   - Calculated as `days_shipping_real - days_shipping_scheduled` across all 180,519 items. Because 73,788 items arrived on-time or early, the net algebraic variance is only +0.57 days.
> 
> - **Positive Delay Severity (+1.62 days):**
>   - Calculated strictly on the 98,977 shipments that actually breached their SLA (`delay_days > 0`). When a shipment is late, it arrives on average **1.62 days late** (with a **median of 1.00 day**).
> 
> Analyzing the distribution of late shipments revealed that:
> - **58.56% (57,957 items)** are late by exactly **1 day**.
> - **27.84% (27,551 items)** are late by **2 days**.
> - Together, **86.4% of all delays are within 1 to 2 days**.
> 
> This is a crucial finding for manufacturing logistics like Volvo: delays are not catastrophic multi-week carrier disappearances; they are narrow 24-to-48 hour window breaches, which are easily correctable by tightening dispatch cut-off times and adjusting lead-time promises."*

---

### Q4: "What was the most counter-intuitive finding in the dataset, and what action would you recommend?"
**Model Answer:**
> *"The most counter-intuitive insight was that premium expedited shipping modes suffered the worst on-time performance:
> - **First Class:** 95.32% Late (only 4.68% On-Time)
> - **Second Class:** 76.63% Late (only 23.37% On-Time)
> - **Standard Class:** 38.07% Late (61.93% On-Time)
> 
> Looking deeper into the root cause:
> - First Class orders were scheduled with a 1-day transit commitment (`days_shipping_scheduled = 1`), but physical transit took **2.00 days** on average.
> - Second Class promised 2 days, but physical transit took **3.99 days**.
> - Standard Class promised 4 days, and physical transit averaged **4.00 days**.
> 
> The carriers were delivering First Class shipments in 2 days (twice as fast as Standard Class), but they were flagged as 'late' 95% of the time because the Sales and Order Management Systems committed to an impossible 1-day delivery window.
> 
> **Recommendation:** Update the ERP/order management scheduling rules to promise realistic SLAs (First Class: 2 days; Second Class: 4 days; Standard Class: 4-5 days). This eliminates artificial SLA failure metrics and customer frustration immediately, without spending extra capital on freight."*

---

### Q5: "How does the International Trade & Customs Compliance companion extension connect to Volvo Group's operations?"
**Model Answer:**
> *"Volvo Group manufactures commercial vehicles, buses, and construction equipment that require high-velocity cross-border supply chains. In automotive assembly, parts must clear customs seamlessly under exact Harmonized System (HS) classifications. 
> 
> Real customs declarations and commercial invoices are legally confidential corporate assets. To demonstrate full customs analytics competence without fabricating unverified data, I created a modular, reproducible extension (`src/customs_enrichment.py`, deterministic seed 42) mapped 1:1 to unique orders:
> 
> 1. **HS Tariff Classifications:** Mapped items to core automotive WCO chapters:
>    - **Chapter 84 (Nuclear reactors, boilers, machinery; e.g., engines, pumps, transmissions)**
>    - **Chapter 85 (Electrical machinery; e.g., ECUs, sensors, wiring harnesses)**
>    - **Chapter 87 (Vehicles and automotive parts; e.g., chassis, truck cabs, brake assemblies)**
> 
> 2. **Customs Risk Routing Channels:** Modeled the standard World Customs Organization risk channels:
>    - **Green Channel (Automated Clearance):** ~70% of shipments, average dwell time 1.2 days, 0% inspection hold rate.
>    - **Yellow Channel (Documentary Review):** ~20% of shipments, average dwell time 2.8 days.
>    - **Red Channel (Physical Inspection):** ~10% of shipments, average dwell time 5.1 days, 100% physical inspection.
> 
> 3. **Demurrage Cost Governance:** Modeled container storage demurrage at standard maritime rates ($185/day for dwell times exceeding 3 free port storage days), isolating financial exposure from customs clearance bottlenecks.
> 
> All synthetic fields are explicitly prefixed with `sim_` and documented in `docs/synthetic_data_lineage.md` so that simulated customs data is never conflated with real DataCo fulfillment observations."*

---

### Q6: "How did you ensure data integrity and prevent metric drift between Python, MySQL, and Power BI?"
**Model Answer:**
> *"Metric drift between data pipelines and business dashboards is one of the most common reasons leadership loses trust in analytics. I implemented three layers of defense:
> 
> 1. **Zero-Silent-Drop Ingestion:** Enforced row-count assertions in Python (`src/clean_pipeline.py`) validating that input rows (180,519) match output rows (180,519) across raw CSV, parquet, and database tables.
> 2. **Relational Referential Integrity:** Built foreign key constraints across the Star Schema and wrote automated SQL integrity audits (Query 6) confirming 0 orphan foreign keys, 0 inverted timestamps (`shipping_date < order_date`), and 0 negative prices.
> 3. **Automated Cross-Engine Pytest Suite:** Developed `tests/test_kpi_consistency.py` and `tests/test_mysql_live.py`, which connect to both the SQLite database and a live running MariaDB/MySQL instance. The test compares SQL aggregations against pandas dataframe calculations on the parquet gold layer, validating that:
>    - Item count (180,519), distinct orders (65,752), gross sales ($36,784,735.01), net profit ($3,966,902.97), contractual OTD (42.71%), and customer OTD (40.88%) match exactly across all engines.
> 
> All 13 automated tests pass in under 1.5 seconds, guaranteeing total reproducibility."*

