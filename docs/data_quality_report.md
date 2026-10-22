# Data Quality & Validation Report

## 1. Executive Summary
- **Execution Timestamp:** `2026-10-22 18:31:59`
- **Input Records:** `180,519`
- **Output Records:** `180,519`
- **Row Retention Rate:** `100.0%` (Zero silent record drops)
- **Primary Grain:** Unique `order_item_id` (1 row = 1 ordered product item)
- **Distinct Orders:** `65,752`
- **Distinct Customers:** `20,652`
- **Distinct Products:** `118` across `50` categories

## 2. Automated Quality Assertion Outcomes

| Quality Check Description | Target Condition | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| Row Count Reconciliation | Input == Output (180,519) | 180,519 | **PASS** |
| Primary Key Uniqueness | `order_item_id` unique | 180,519 unique | **PASS** |
| Temporal Sequencing | `shipping_date >= order_date` | 0 inversions | **PASS** |
| Non-Negative Durations | `days_shipping_real >= 0` | Min: 0 | **PASS** |
| Non-Negative Durations | `days_shipping_scheduled >= 0` | Min: 0 | **PASS** |
| Financial Range Validity | `sales_gross >= 0` | Min: $9.99 | **PASS** |
| Financial Range Validity | `product_price >= 0` | Min: $9.99 | **PASS** |
| Late Delivery Logic Consistency | `Late delivery == (delay_days > 0)` | 100% agreement (98,977 late) | **PASS** |

## 3. Missing Value Handling & Imputation Policy

| Field | Missing Count | Handling Method | Rationale |
| :--- | :--- | :--- | :--- |
| `Product Description` | 180,519 (100%) | Dropped column | Column was 100% blank in raw source. Product name and category provide sufficient descriptive grain. |
| `Customer Password` / `Email` | 0 | Dropped columns | PII / dummy credentials unnecessary for supply chain analytics. |
| `Customer Lname` | 8 (0.004%) | Imputed with `'Unknown'` | Negligible fraction; preserving row preserves order integrity. |
| `Customer Zipcode` | 3 (0.001%) | Imputed with `'UNKNOWN'` | Geo analysis relies primarily on City, State, Country, and Market. |
| `Order Zipcode` | 155,679 (86.2%) | Imputed with `'UNKNOWN'` | Destination analysis utilizes `order_city`, `order_state`, `order_country`, and `order_region`. |

## 4. Key Performance Indicators & Dual OTD Metrics

For the complete, rigorous KPI reconciliation across Python, SQLite, MySQL, and Power BI, refer to [kpi_audit.md](file:///docs/kpi_audit.md).

### Dual On-Time Delivery (OTD) Benchmarks:
- **Contractual Carrier SLA OTD Rate (Shipped Base):** `42.71%` (73,788 on-time / 172,765 shipped items)
  - *Denominator excludes 7,754 canceled orders.* Evaluates physical carrier execution against contractual service commitments.
- **Customer Fulfillment OTD Rate (Placed Base):** `40.88%` (73,788 on-time / 180,519 total placed items)
  - *Denominator includes cancellations as non-fulfilled orders.* Evaluates overall business promise-to-delivery reliability from the customer perspective.
- **Order-Level Fulfillment OTD (Consignment Grain):** `42.69%` (26,849 / 62,897 shipped orders where 100% of line items arrived on time).

### Delay Metrics & Distribution:
- **Delay Variance (All Shipments):** `+0.57 days` (Mean difference `days_shipping_real - days_shipping_scheduled` incorporating advance and on-time shipments).
- **Positive Delay Severity (Late Shipments Only, N = 98,977):** `+1.62 days` (Median: `1.00 days`, Max: `4.00 days`).
- **Late Duration Frequency Breakdown:**
  - 1 Day Late: `57,957 items` (**58.56%** of late shipments)
  - 2 Days Late: `27,551 items` (**27.84%** of late shipments)
  - 3 Days Late: `6,774 items` (**6.84%** of late shipments)
  - 4 Days Late: `6,695 items` (**6.77%** of late shipments)

### Commercial & Financial Totals:
- **Total Order Items:** `180,519`
- **Total Gross Sales:** `$36,784,735.01` (Commercial value, real DataCo)
- **Total Order Profit:** `$3,966,902.97` (Commercial profit, real DataCo)
- **Canceled Orders:** `7,754 items` (4.30% of items) with `$1,570,305.10` sales value.

## 5. Shipping Mode Breakdown & SLA Miscalibration

| shipping_mode   |   Items |   Late_Items |   Avg_Real_Days |   Avg_Sched_Days |   Late_Rate_% | Contractual_OTD_% |
|:----------------|--------:|-------------:|----------------:|-----------------:|--------------:|------------------:|
| First Class     |   27814 |        26513 |        2.000000 |                1 |         95.32 |              4.68 |
| Same Day        |    9737 |         4454 |        0.478279 |                0 |         45.74 |             54.26 |
| Second Class    |   35216 |        26987 |        3.990830 |                2 |         76.63 |             23.37 |
| Standard Class  |  107752 |        41023 |        3.995910 |                4 |         38.07 |             61.93 |

