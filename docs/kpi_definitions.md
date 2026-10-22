# Business KPI Definitions & Formulation Guide

This document establishes the official enterprise definitions, mathematical formulas, numerators, denominators, inclusion/exclusion criteria, and grain for all Key Performance Indicators (KPIs) in the Supply Chain & International Trade Analytics platform.

---

## 1. Logistics Delivery & SLA Metrics (Ground Truth Core)

### KPI 1A: On-Time Delivery Rate — Contractual Shipped Base (42.71%)
* **Business Objective:** Measure the proportion of completed shipments that arrived on or before the committed scheduled delivery deadline.
* **Grain:** Order Item (`order_item_id`).
* **Numerator:** Count of order items where `days_shipping_real <= days_shipping_scheduled` AND `is_canceled = 0`.
* **Denominator:** Total order items shipped (excluding canceled orders): $N = 180,519 - 7,754 = 172,765$.
  $$\text{OTD Rate (Shipped Base \%)} = \frac{\sum [\text{is\_on\_time} = 1]}{\sum [\text{is\_canceled} = 0]} \times 100 = \frac{73,788}{172,765} \times 100 = \mathbf{42.71\%}$$
* **Operational Usage:** Evaluates 3PL freight carrier transit performance strictly on freight that was dispatched and moved.

### KPI 1B: On-Time Delivery Rate — Customer Placed Base (40.88%)
* **Business Objective:** Measure end-to-end customer order fulfillment reliability, penalizing canceled and unfulfilled orders as service failures.
* **Grain:** Order Item (`order_item_id`).
* **Numerator:** Count of order items delivered on-time (`is_on_time = 1`).
* **Denominator:** Total order items placed: $N = 180,519$.
  $$\text{OTD Rate (Total Base \%)} = \frac{\sum [\text{is\_on\_time} = 1]}{\text{Total Items}} \times 100 = \frac{73,788}{180,519} \times 100 = \mathbf{40.88\%}$$
* **Order-Level (Consignment Grain):** $\frac{\text{Orders with 100\% on-time items}}{\text{Total Shipped Orders}} = \frac{26,849}{62,897} = \mathbf{42.69\%}$.

---

### KPI 2: Late Delivery Rate (57.29% Shipped / 54.83% Placed)
* **Business Objective:** Measure the frequency of deliveries that breached the promised transit SLA.
* **Grain:** Order Item (`order_item_id`).
* **Formula (Shipped Base):**
  $$\text{Late Delivery Rate (Shipped Base \%)} = \frac{\sum [\text{is\_late} = 1]}{\sum [\text{is\_canceled} = 0]} \times 100 = \frac{98,977}{172,765} \times 100 = \mathbf{57.29\%}$$
* **Formula (Total Placed Base):**
  $$\text{Late Delivery Rate (Total Base \%)} = \frac{\sum [\text{is\_late} = 1]}{\text{Total Items}} \times 100 = \frac{98,977}{180,519} \times 100 = \mathbf{54.83\%}$$

---

### KPI 3A: Positive Late-Delivery Delay (+1.62 Days)
* **Business Objective:** Measure the magnitude of delay strictly for shipments that suffered an SLA breach (`is_late = 1`).
* **Grain:** Late order items ($N = 98,977$).
* **Formula:**
  $$\text{Positive Delay} = \frac{\sum_{\text{late}} (\text{days\_shipping\_real} - \text{days\_shipping\_scheduled})}{N_{\text{late}}} = \frac{160,377}{98,977} = \mathbf{+1.62 \text{ days}}$$
  $$\text{Median Delay} = \mathbf{1.00 \text{ day}}$$
* **Delay Frequency Distribution (Late Shipments):**
  * Delayed by 1 day: **57,957 items (58.56%)**
  * Delayed by 2 days: **27,551 items (27.84%)**
  * Delayed by 3 days: **6,772 items (6.84%)**
  * Delayed by 4 days: **6,697 items (6.77%)**

### KPI 3B: Overall Delay Variance (+0.57 Days)
* **Business Objective:** Algebraic deviation between actual days and scheduled days ($\text{real} - \text{scheduled}$) across **all** shipments, incorporating advance shipments (negative values) and on-time shipments (zero).
* **Grain:** Order Item ($N = 180,519$).
* **Formula:**
  $$\text{Delay Variance} = \frac{\sum (\text{days\_shipping\_real} - \text{days\_shipping\_scheduled})}{\text{Total Items}} = \frac{103,485}{180,519} = \mathbf{+0.57 \text{ days}}$$
* **All-Shipment Distribution:**
  * Ahead by 2 days: 21,666 items (12.00%)
  * Ahead by 1 day: 21,700 items (12.02%)
  * On-Time (0 days): 33,753 items (18.70%)
  * Delayed by 1 to 4 days: 103,400 items (57.28% including canceled with recorded transit days)

---

### KPI 4: Shipping-Mode SLA vs. Actual Transit Lead Time
* **Business Objective:** Contrast promised customer lead times with physical transit execution across shipping modes.
* **Important Terminology Note:** In the core real dataset, only **Shipping Mode** is available. Specific carrier identities are not present in raw DataCo.
* **Formulas:**
  $$\text{Mean Scheduled Transit} = \frac{1}{N} \sum \text{days\_shipping\_scheduled} = \mathbf{2.93 \text{ days}}$$
  $$\text{Mean Actual Transit} = \frac{1}{N} \sum \text{days\_shipping\_real} = \mathbf{3.50 \text{ days}}$$
* **Ground Truth Baselines by Shipping Mode:**
  * **First Class:** Scheduled SLA = 1.00d | Actual Transit = 2.00d | Variance = +1.00d | **Late Rate = 95.32%**
  * **Second Class:** Scheduled SLA = 2.00d | Actual Transit = 3.99d | Variance = +1.99d | **Late Rate = 76.63%**
  * **Same Day:** Scheduled SLA = 0.00d | Actual Transit = 0.48d | Variance = +0.48d | **Late Rate = 45.74%**
  * **Standard Class:** Scheduled SLA = 4.00d | Actual Transit = 4.00d | Variance = -0.00d | **Late Rate = 38.07%**

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
