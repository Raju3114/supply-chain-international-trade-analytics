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

## 4. Key Performance Indicators (Core Ground Truth)

- **Total Order Items:** 180,519
- **Late Deliveries:** 98,977 (54.83% of all items)
- **On-Time Deliveries:** 73,788 (40.88% of all items)
- **Average Delay for Late Shipments:** `1.62 days` (Median: `1.0 days`)
- **Total Gross Sales:** `$36,784,735.01`
- **Total Order Profit:** `$3,966,902.97`

## 5. Shipping Mode Breakdown

| shipping_mode   |   Items |   Late_Items |   Avg_Real_Days |   Avg_Sched_Days |   Late_Rate_% |
|:----------------|--------:|-------------:|----------------:|-----------------:|--------------:|
| First Class     |   27814 |        26513 |        2        |                1 |         95.32 |
| Same Day        |    9737 |         4454 |        0.478279 |                0 |         45.74 |
| Second Class    |   35216 |        26987 |        3.99083  |                2 |         76.63 |
| Standard Class  |  107752 |        41023 |        3.99591  |                4 |         38.07 |
