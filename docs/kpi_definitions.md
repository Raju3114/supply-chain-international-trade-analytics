# Business KPI Definitions & Formulation Guide

This document establishes the official enterprise definitions, mathematical formulas, numerators, denominators, inclusion/exclusion criteria, and grain for all Key Performance Indicators (KPIs) in the Supply Chain & International Trade Analytics platform.

---

## 1. Logistics Delivery & SLA Metrics (Ground Truth Core)

### KPI 1: On-Time Delivery Rate (OTD %)
* **Business Objective:** Measure the proportion of shipments delivered on or before the committed scheduled delivery deadline.
* **Grain:** Order Item (`order_item_id`).
* **Numerator:** Count of order items where `days_shipping_real <= days_shipping_scheduled` AND `delivery_status != 'Shipping canceled'`.
* **Denominator:** Total order items shipped (including or excluding cancellations depending on SLA contract; standard formula excludes cancellations).
  $$\text{OTD Rate (\%)} = \frac{\sum [\text{days\_shipping\_real} \le \text{days\_shipping\_scheduled} \land \text{delivery\_status} \neq \text{'Shipping canceled'}]}{\sum [\text{order\_item\_id}]} \times 100$$
* **Current Ground Truth Baseline:** **40.88%** across all items (or **42.71%** when excluding canceled items).
* **Treatment of Exceptions:** Canceled shipments are categorized under `Shipping canceled` (4.30% of items) and are treated as non-deliveries.

---

### KPI 2: Late Delivery Rate (%)
* **Business Objective:** Measure the frequency of deliveries that breached the promised transit SLA.
* **Grain:** Order Item (`order_item_id`).
* **Numerator:** Count of order items with `delivery_status = 'Late delivery'` (which strictly corresponds to `days_shipping_real > days_shipping_scheduled` for completed shipments).
* **Denominator:** Total order items.
  $$\text{Late Delivery Rate (\%)} = \frac{\sum [\text{is\_late} = 1]}{\sum [\text{order\_item\_id}]} \times 100$$
* **Current Ground Truth Baseline:** **54.83%** (98,977 items).

---

### KPI 3: Average & Median Delay Variance
* **Business Objective:** Quantify the magnitude of SLA failure in calendar days for shipments that were delayed.
* **Grain:** Late order items (`is_late = 1`).
* **Formula:**
  $$\text{Delay Days} = \text{days\_shipping\_real} - \text{days\_shipping\_scheduled}$$
  $$\text{Average Delay} = \frac{\sum_{\text{late}} (\text{delay\_days})}{N_{\text{late}}}$$
* **Current Ground Truth Baseline:**
  * **Mean Delay (Late Shipments):** `1.62 days`
  * **Median Delay (Late Shipments):** `1.00 days`
  * **Overall Mean Delay (All Shipments):** `0.57 days`

---

### KPI 4: Lead-Time SLA Discrepancy
* **Business Objective:** Contrast promised customer lead times with physical transit execution across shipping modes.
* **Formulas:**
  $$\text{Mean Scheduled Transit} = \frac{1}{N} \sum \text{days\_shipping\_scheduled}$$
  $$\text{Mean Actual Transit} = \frac{1}{N} \sum \text{days\_shipping\_real}$$
* **Current Ground Truth Baselines by Shipping Mode:**
  * **First Class:** Scheduled SLA = 1.00 day | Actual Transit = 2.00 days | Delay Variance = +1.00 day (95.32% Late)
  * **Second Class:** Scheduled SLA = 2.00 days | Actual Transit = 3.99 days | Delay Variance = +1.99 days (76.63% Late)
  * **Standard Class:** Scheduled SLA = 4.00 days | Actual Transit = 4.00 days | Delay Variance = -0.00 days (38.07% Late)
  * **Same Day:** Scheduled SLA = 0.00 days | Actual Transit = 0.48 days | Delay Variance = +0.48 days (45.74% Late)

---

## 2. Order & Commercial Operations Metrics

### KPI 5: Order Item Volume & Order Multiplier
* **Business Objective:** Track transaction throughput and cart depth.
* **Order Item Volume:** Total row count in `fact_shipments` ($N = 180,519$).
* **Distinct Order Count:** Distinct count of `order_id` ($N = 65,752$).
* **Average Items Per Order:**
  $$\text{Items per Order} = \frac{180,519}{65,752} = 2.75 \text{ items/order}$$

---

### KPI 6: Commercial Gross Sales & Realized Margin
* **Business Objective:** Monitor top-line revenue and operating benefit across destination markets.
* **Gross Sales (USD):** Total item sales before discount:
  $$\text{Gross Sales} = \sum (\text{sales\_gross}) = \$36,784,735.01$$
* **Net Profit (USD):** Operating benefit per order:
  $$\text{Total Profit} = \sum (\text{benefit\_per\_order}) = \$3,966,902.97$$
* **Commercial Net Profit Margin (%):**
  $$\text{Profit Margin (\%)} = \frac{\$3,966,902.97}{\$36,784,735.01} \times 100 = 10.78\%$$
* **Cost Clarification Note:** Product sales and profits represent retail and commercial transaction values, **not** isolated carrier freight invoices. Dedicated freight and customs expenses are addressed in the international extension.

---

### KPI 7: Operational Exception Rate (Risk & Fraud Exposure)
* **Business Objective:** Track items held or interrupted due to risk management.
* **Suspected Fraud Rate:**
  $$\text{Fraud Rate (\%)} = \frac{\sum [\text{order\_status} = \text{'SUSPECTED\_FRAUD'}]}{\text{Total Items}} \times 100 = \frac{4,062}{180,519} \times 100 = 2.25\%$$
* **Cancellation Rate:**
  $$\text{Cancellation Rate (\%)} = \frac{\sum [\text{order\_status} = \text{'CANCELED'}]}{\text{Total Items}} \times 100 = \frac{3,692}{180,519} \times 100 = 2.05\%$$

---

## 3. Synthetic International Trade & Customs Extension KPIs (Phase 2)

*The following metrics apply exclusively to the clearly labeled Phase 2 companion extension:*

### KPI 8: Customs Dwell Time (Days) `[SIMULATED]`
* **Definition:** Calendar days between port of entry arrival and official customs broker release.
  $$\text{Dwell Time} = \text{sim\_customs\_release\_date} - \text{sim\_port\_arrival\_date}$$
* **Thresholds:** Dwell > 3 days triggers demurrage exposure alert.

### KPI 9: Documentation Discrepancy Rate (%) `[SIMULATED]`
* **Definition:** Percentage of international consignments flagged with commercial invoice discrepancies or missing certificates of origin.
  $$\text{Doc Exception Rate} = \frac{\sum [\text{sim\_doc\_discrepancy\_flag} = 1]}{\text{Total International Consignments}} \times 100$$

### KPI 10: Customs Inspection Hit Rate (%) `[SIMULATED]`
* **Definition:** Proportion of shipments routed to red-channel physical examination vs green-channel automated clearance.
