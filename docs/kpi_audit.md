# KPI Implementation Audit & Lineage Matrix

This document provides a line-by-line verification audit of every KPI across the analytics platform, documenting its implementation status, mathematical formula, denominator, aggregation grain, lineage classification, test coverage, and dashboard exposure.

---

## 1. Master KPI Audit Table

| KPI Name | Status | Source Table(s) & Column(s) | Exact Calculation & Denominator | Grain | Lineage Type | Automated Test Coverage | Dashboard Visibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **On-Time Delivery Rate (Shipped Base)** | **IMPLEMENTED & TESTED** | `fact_shipments` (`is_on_time`, `is_canceled`) | $\frac{\sum [\text{is\_on\_time}=1]}{\sum [\text{is\_canceled}=0]} \times 100 = \frac{73,788}{172,765} = 42.71\%$ | Order Item | `[DERIVED]` | `test_kpi_consistency.py` | Page 1 & Page 2 (Primary Carrier SLA KPI) |
| **On-Time Delivery Rate (Total Placed Base)** | **IMPLEMENTED & TESTED** | `fact_shipments` (`is_on_time`, `order_item_id`) | $\frac{\sum [\text{is\_on\_time}=1]}{\text{Total Items}} \times 100 = \frac{73,788}{180,519} = 40.88\%$ | Order Item | `[DERIVED]` | `test_kpi_consistency.py` | Page 1 (Customer Fulfillment Funnel) |
| **Late Delivery Rate (Shipped Base)** | **IMPLEMENTED & TESTED** | `fact_shipments` (`is_late`, `is_canceled`) | $\frac{\sum [\text{is\_late}=1]}{\sum [\text{is\_canceled}=0]} \times 100 = \frac{98,977}{172,765} = 57.29\%$ | Order Item | `[DERIVED]` | `test_kpi_consistency.py` | Page 2 |
| **Late Delivery Rate (Total Placed Base)** | **IMPLEMENTED & TESTED** | `fact_shipments` (`is_late`, `order_item_id`) | $\frac{\sum [\text{is\_late}=1]}{\text{Total Items}} \times 100 = \frac{98,977}{180,519} = 54.83\%$ | Order Item | `[DERIVED]` | `test_kpi_consistency.py` | Page 1 & Page 2 (Executive Overview) |
| **Order-Level On-Time Rate (Consignment)** | **IMPLEMENTED & TESTED** | `fact_shipments` (`order_id`, `is_on_time`) | $\frac{\text{Orders where ALL items on-time}}{\text{Total Shipped Orders}} = \frac{26,849}{62,897} = 42.69\%$ | Order (Consignment) | `[DERIVED]` | `test_kpi_consistency.py` | Documented in EDA & KPI Guide |
| **Positive Late-Delivery Delay** | **IMPLEMENTED & TESTED** | `fact_shipments` (`delay_days`, `is_late`) | $\frac{\sum_{\text{late}} \text{delay\_days}}{N_{\text{late}}} = \frac{160,377}{98,977} = +1.62 \text{ days}$ (Median: 1.0d) | Late Items (`is_late=1`) | `[DERIVED]` | `test_kpi_consistency.py` | Page 2 (Delay Severity Card) |
| **Overall Delay Variance** | **IMPLEMENTED & TESTED** | `fact_shipments` (`delay_days`) | $\frac{\sum \text{delay\_days}}{\text{Total Items}} = \frac{103,485}{180,519} = +0.57 \text{ days}$ (Median: 1.0d) | Order Item | `[DERIVED]` | `test_kpi_consistency.py` | Page 2 & SQL Query 1 |
| **Scheduled Lead Time (SLA)** | **IMPLEMENTED & TESTED** | `fact_shipments` (`days_shipping_scheduled`) | $\text{Mean}(\text{days\_shipping\_scheduled}) = 2.93 \text{ days}$ | Order Item | `[ORIGINAL]` | `test_data_pipeline.py` | Page 2 (SLA vs Actual Transit Chart) |
| **Actual Transit Lead Time** | **IMPLEMENTED & TESTED** | `fact_shipments` (`days_shipping_real`) | $\text{Mean}(\text{days\_shipping\_real}) = 3.50 \text{ days}$ | Order Item | `[ORIGINAL]` | `test_data_pipeline.py` | Page 2 (SLA vs Actual Transit Chart) |
| **Total Order Item Volume** | **IMPLEMENTED & TESTED** | `fact_shipments` (`order_item_id`) | $\text{COUNT}(order\_item\_id) = 180,519 \text{ items}$ | Order Item | `[ORIGINAL]` | `test_clean_row_count` | Page 1 (Volume Card) |
| **Total Distinct Orders** | **IMPLEMENTED & TESTED** | `fact_shipments` (`order_id`) | $\text{DISTINCTCOUNT}(order\_id) = 65,752 \text{ orders}$ | Order (Consignment) | `[ORIGINAL]` | `test_clean_row_count` | Page 1 & Page 3 |
| **Average Items Per Order** | **IMPLEMENTED & TESTED** | `fact_shipments` (`order_item_id`, `order_id`) | $\frac{180,519}{65,752} = 2.75 \text{ items/order}$ | Ratio | `[DERIVED]` | Reconciled in Pipeline | Page 1 |
| **Gross Commercial Sales** | **IMPLEMENTED & TESTED** | `fact_shipments` (`sales_gross`) | $\sum (\text{sales\_gross}) = \$36,784,735.01$ | Order Item | `[ORIGINAL]` | `test_kpi_consistency.py` | Page 1 (Gross Sales Card) |
| **Operating Profit** | **IMPLEMENTED & TESTED** | `fact_shipments` (`benefit_per_order`) | $\sum (\text{benefit\_per\_order}) = \$3,966,902.97$ | Order Item | `[ORIGINAL]` | `test_kpi_consistency.py` | Page 1 (Operating Profit Card) |
| **Operating Profit Margin %** | **IMPLEMENTED & TESTED** | `fact_shipments` (`benefit_per_order`, `sales_gross`)| $\frac{\$3,966,902.97}{\$36,784,735.01} \times 100 = 10.78\%$ | Aggregate Ratio | `[DERIVED]` | Verified in Python & SQL | Page 1 (Margin Indicator) |
| **Order Cancellation Rate** | **IMPLEMENTED & TESTED** | `fact_shipments` (`is_canceled`) | $\frac{7,754}{180,519} \times 100 = 4.30\% \text{ (Items)}; \frac{2,855}{65,752} \times 100 = 4.34\% \text{ (Orders)}$ | Order Item & Order | `[DERIVED]` | `test_data_pipeline.py` | Page 1 (Fulfillment Funnel) |
| **Suspected Fraud Rate** | **IMPLEMENTED & TESTED** | `fact_shipments` (`order_status`) | $\frac{4,062}{180,519} \times 100 = 2.25\%$ ($825,935 exposure) | Order Item | `[ORIGINAL]` | SQL Query 5 | Page 1 (Risk Exception Funnel) |
| **Actual Freight Cost** | ❌ **UNAVAILABLE IN REAL DATA** | None (Real DataCo dataset lacks freight expense) | N/A — Strictly documented limitation. Never presented as real. | N/A | **N/A** | Schema verified | Labeled as unavailable in docs |
| **Simulated Freight Cost USD** | **IMPLEMENTED & TESTED** | `fact_customs_declarations` (`sim_freight_cost_usd`) | $\text{Weight (kg)} \times \text{Rate/kg by Mode/Lane}$ | Order (Consignment) | `[SIMULATED]` | `test_synthetic_customs` | Page 5 (Customs & Logistics Cost) |
| **Customs Clearance Dwell Time** | **IMPLEMENTED & TESTED** | `fact_customs_declarations` (`sim_dwell_time_days`) | $\text{Release Timestamp} - \text{Port Arrival Timestamp}$ | Order (Consignment) | `[SIMULATED]` | `test_synthetic_customs` | Page 5 (Dwell Time Card & Chart) |
| **Demurrage Penalty Incurred** | **IMPLEMENTED & TESTED** | `fact_customs_declarations` (`sim_demurrage_incurred_usd`)| $\text{MAX}(0, \text{dwell} - 3.0) \times \$185/\text{day} = \$2.21\text{M}$ | Order (Consignment) | `[SIMULATED]` | `test_synthetic_customs` | Page 5 (Demurrage Exposure Card) |
| **Documentation Discrepancy %** | **IMPLEMENTED & TESTED** | `fact_customs_declarations` (`sim_doc_discrepancy_flag`)| $\frac{\sum [\text{sim\_doc\_discrepancy}=1]}{65,752} \times 100 = 5.85\%$ | Order (Consignment) | `[SIMULATED]` | `test_synthetic_customs` | Page 5 (Compliance Risk Metric) |
| **Inspection Hit Rate (Red Channel)**| **IMPLEMENTED & TESTED**| `fact_customs_declarations` (`sim_inspection_channel`)| $\frac{\sum [\text{channel}=\text{'Red'}]}{65,752} \times 100 = 4.84\%$ | Order (Consignment) | `[SIMULATED]` | `test_synthetic_customs` | Page 5 (Customs Risk Routing) |

---

## 2. Key Audit Insights & Methodological Distinctions

### A. The Two On-Time Delivery Rates
1. **Contractual Carrier On-Time Rate (Shipped Base = 42.71%):**
   * Excludes canceled orders ($7,754$ items / $2,855$ orders) where physical transit never finished.
   * Directly reflects 3PL freight carrier SLA execution.
2. **Customer Fulfillment On-Time Rate (Placed Order Base = 40.88%):**
   * Treats canceled orders as failed fulfillment events from the customer perspective.
   * Useful for executive supply chain customer service reviews.

### B. Delay Variance vs. Positive Delay
* **Delay Variance (+0.57 days):** Represents the algebraic deviation between actual days and scheduled days ($\text{real} - \text{scheduled}$) across **all** shipments, including advance shipments (e.g. $-1, -2$ days) and on-time shipments ($0$ days).
* **Positive Late Delay (+1.62 days):** Isolates strictly the delayed shipments ($\text{delay\_days} > 0$), quantifying how late delayed shipments are on average. Median late delay is $1.00$ day.

### C. Transparency on Shipping Costs and Carriers
* **Zero Freight Cost Ingestion:** The real DataCo dataset contains **zero** freight cost or carrier invoice line items. Product prices and profit metrics are commercial retail figures, not transportation costs.
* **Shipping Modes vs. Carriers:** Real data specifies only the mode (*Standard Class, First Class, Second Class, Same Day*). Specific carrier assignments (Maersk, MSC, DHL, Kuehne+Nagel) exist **only** within the clearly labeled Phase 2 simulation companion table.
