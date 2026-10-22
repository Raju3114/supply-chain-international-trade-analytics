# Technical Interview Preparation & Resume Impact Guide

This guide prepares you to speak authoritatively about this project in technical interviews, specifically for Supply Chain Analytics, Data Engineering, and International Trade Operations roles (such as Volvo Group India's Custom & Trade International department).

---

## 1. Truthful Resume Bullets (Ground Truth Backed)

Add these high-impact, truthful bullet points to your resume:

* **Supply Chain Analytics & Data Engineering:**
  > *"Engineered an end-to-end supply chain analytics pipeline processing 180,519 order items ($36.78M gross volume) using Python, SQLite, and MySQL; uncovered an operational SLA miscalibration causing a 95.3% late delivery rate in expedited freight modes and formulated data-backed lead-time re-calibrations."*

* **Relational Modeling & Advanced SQL:**
  > *"Designed and deployed a 3NF-to-Star-Schema dimensional model across 6 tables with 100% referential integrity; implemented advanced SQL analytical suites utilizing CTEs, window functions (`DENSE_RANK`, `AVG OVER`), and multi-table joins to monitor On-Time In-Full (OTIF) rates across 5 global markets."*

* **International Trade & Customs Compliance Simulation:**
  > *"Developed a modular customs compliance extension modeling WCO Harmonized System classifications (Chapters 84, 85, 87), port entry dwell times, and risk routing channels; built automated validation suites reconciling KPIs across Python, SQL, and Power BI with zero metric drift."*

---

## 2. Technical Interview Questions & Model Answers

### Q1: "Walk me through the architecture of your supply chain analytics project."
**Model Answer:**
> *"The project follows an industry-standard dimensional modeling lifecycle. I started with a raw transactional supply chain dataset of 180,519 records from Mendeley Data under a CC BY 4.0 license. 
> 
> In the data engineering layer, I built an automated Python cleaning pipeline (`src/clean_pipeline.py`) that enforces snake_case schema naming, handles missing geo data without silent row dropping, parses temporal timestamps, and validates mathematical assertions (e.g., verifying `shipping_date >= order_date` and zero negative durations).
> 
> For the database layer, I designed a Star Schema featuring a central `fact_shipments` table linked to 5 dimension tables (`dim_date`, `dim_product`, `dim_customer_geo`, `dim_shipping_mode`, `dim_order_destination`). I developed native DDL for both MySQL 8.0 and SQLite, incorporating foreign key constraints and composite indexes.
> 
> Finally, I established a documented DAX library and Power BI reporting model across 5 pages: Executive Overview, Delivery Performance, Regional Logistics, Product Portfolio, and International Customs Dwell Time."*

---

### Q2: "What was the most surprising operational insight you discovered during Exploratory Data Analysis?"
**Model Answer:**
> *"The most significant insight was a massive SLA miscalibration in expedited shipping modes. Intuitively, one would assume premium shipping modes like First Class have the lowest late delivery rate. However, the data revealed that First Class had a staggering 95.32% late delivery rate, and Second Class had 76.63%, compared to Standard Class at only 38.07%.
> 
> When I investigated the root cause, I found that the scheduled commitment for First Class was rigidly set to 1 day, while actual physical carrier transit averaged 2.00 days. Similarly, Second Class promised 2 days but physically took 3.99 days. 
> 
> This taught me a vital business lesson: carriers were not physically failing or slowing down; rather, the sales and order management systems were over-promising unachievable transit SLAs. My strategic recommendation was to re-calibrate promised SLAs in the order management system (First Class to 2 days, Second Class to 4 days), which immediately resolves artificial SLA breach penalties without increasing logistics costs."*

---

### Q3: "How did you maintain data integrity and handle data quality exceptions?"
**Model Answer:**
> *"I maintained a strict policy against silent data loss:
> 1. In `Customer Zipcode` (3 missing) and `Customer Lname` (8 missing), I imputed with sentinel values (`'UNKNOWN'`) rather than dropping rows, ensuring 100% row retention (180,519 in, 180,519 out).
> 2. `Product Description` was 100% null in the raw source, so I explicitly dropped the column while retaining `product_name` and `category_name`.
> 3. I discovered that 7,754 orders had a status of `Shipping canceled`, where actual shipping days were still recorded. I decoupled canceled orders into a distinct boolean indicator (`is_canceled`), ensuring they are partitioned cleanly from `is_late` and `is_on_time`.
> 4. In SQL Query 6, I wrote an automated relational exception audit checking for orphan keys, inverted timestamps, and negative sales, proving 0 integrity violations."*

---

### Q4: "How does the international customs and trade extension relate to automotive operations like Volvo Group?"
**Model Answer:**
> *"In global automotive and heavy machinery manufacturing, supply chains are cross-border and depend heavily on customs clearance. A 2-day port dwell delay on engines or ECUs can halt an assembly line. 
> 
> Because real corporate customs filings contain confidential tariff values and business secrets, I designed a modular, deterministically generated companion extension using Python (`src/customs_enrichment.py`, seed 42) mapped 1-to-1 to each order. 
> 
> I simulated WCO Harmonized System chapters specifically relevant to commercial vehicles: Chapter 84 (Diesel engines, transmissions), Chapter 85 (ECUs, wiring harnesses), and Chapter 87 (Cabin assemblies, truck wheels). I modeled three customs risk channels (Green automated release, Yellow documentary review, Red physical inspection), showing how documentation discrepancies increase port dwell times and incur container demurrage penalties ($185/day beyond free storage limits). 
> 
> This allowed me to build executive dashboards demonstrating customs clearance cycle times, demurrage exposure, and carrier SLA adherence."*

---

### Q5: "How did you ensure that metrics matched between Python, SQL, and Power BI?"
**Model Answer:**
> *"Metric drift between data engineering and business intelligence is a common enterprise failure. To prevent this, I wrote an automated cross-system test suite using pytest (`tests/test_kpi_consistency.py`). 
> 
> The test queries the SQLite analytical database and compares metrics directly against pandas dataframe calculations on the raw parquet layer. It validates that total items (180,519), distinct orders (65,752), on-time delivery rate (40.88%), late rate (54.83%), gross sales ($36,784,735.01), and net operating profit ($3,966,902.97) match identically to two decimal places across both engines."*
