# Power BI DAX Measure Library

This document contains the verified DAX measures implemented for the Supply Chain & International Trade Analytics Dashboard across all five reporting pages.

---

## 1. Core Volume & Commercial Measures

```dax
-- Total Order Item Volume (Base Granularity)
Total Order Items = COUNTROWS(fact_shipments)

-- Distinct Order Count
Total Orders = DISTINCTCOUNT(fact_shipments[order_id])

-- Average Items Per Order
Items Per Order = DIVIDE([Total Order Items], [Total Orders], 0)

-- Gross Sales (USD)
Total Gross Sales = SUM(fact_shipments[sales_gross])

-- Total Operating Profit (USD)
Total Profit = SUM(fact_shipments[benefit_per_order])

-- Commercial Profit Margin %
Profit Margin % = DIVIDE([Total Profit], [Total Gross Sales], 0)

-- Total Discount Value (USD)
Total Discount = SUM(fact_shipments[order_item_discount])

-- Average Product Price
Avg Product Price = AVERAGE(fact_shipments[product_price])
```

---

## 2. Logistics & Delivery Performance Measures

```dax
-- On-Time Delivery Count (Excludes Canceled)
On-Time Deliveries = 
CALCULATE(
    COUNTROWS(fact_shipments),
    fact_shipments[is_on_time] = 1
)

-- Late Delivery Count
Late Deliveries = 
CALCULATE(
    COUNTROWS(fact_shipments),
    fact_shipments[is_late] = 1
)

-- Canceled Shipment Count
Canceled Deliveries = 
CALCULATE(
    COUNTROWS(fact_shipments),
    fact_shipments[is_canceled] = 1
)

-- On-Time Delivery Rate (OTD %)
On-Time Delivery Rate % = 
DIVIDE(
    [On-Time Deliveries],
    [Total Order Items],
    0
)

-- Late Delivery Rate %
Late Delivery Rate % = 
DIVIDE(
    [Late Deliveries],
    [Total Order Items],
    0
)

-- Average Delay Variance (Calendar Days across Late Deliveries)
Avg Delay Days (Late Deliveries) = 
CALCULATE(
    AVERAGE(fact_shipments[delay_days]),
    fact_shipments[is_late] = 1
)

-- Median Delay Days (Late Deliveries)
Median Delay Days (Late Deliveries) = 
CALCULATE(
    MEDIAN(fact_shipments[delay_days]),
    fact_shipments[is_late] = 1
)

-- Scheduled SLA Lead Time (Days)
Avg Scheduled SLA Days = AVERAGE(fact_shipments[days_shipping_scheduled])

-- Actual Transit Duration (Days)
Avg Actual Transit Days = AVERAGE(fact_shipments[days_shipping_real])
```

---

## 3. Time-Intelligence & Trajectory Measures

```dax
-- Sales Year-To-Date (YTD)
Sales YTD = 
CALCULATE(
    [Total Gross Sales],
    DATESYTD(dim_date[full_date])
)

-- Prior Month Sales
Sales Prior Month = 
CALCULATE(
    [Total Gross Sales],
    DATEADD(dim_date[full_date], -1, MONTH)
)

-- Month-over-Month Sales Growth %
Sales MoM Growth % = 
DIVIDE(
    [Total Gross Sales] - [Sales Prior Month],
    [Sales Prior Month],
    0
)

-- Rolling 3-Month On-Time Delivery Rate %
OTD Rate Rolling 3M % = 
CALCULATE(
    [On-Time Delivery Rate %],
    DATESINPERIOD(dim_date[full_date], MAX(dim_date[full_date]), -3, MONTH)
)
```

---

## 4. Phase 2 Synthetic Customs & International Trade Measures

```dax
-- Average Customs Dwell Time at Port of Entry (Days)
[SIM] Avg Customs Dwell Days = 
AVERAGE(fact_customs_declarations[sim_dwell_time_days])

-- Maximum Customs Dwell Time (Days)
[SIM] Max Customs Dwell Days = 
MAX(fact_customs_declarations[sim_dwell_time_days])

-- Total Demurrage Exposure Incurred (USD)
[SIM] Total Demurrage USD = 
SUM(fact_customs_declarations[sim_demurrage_incurred_usd])

-- Demurrage Impacted Shipments Count (Dwell > 3 Free Days)
[SIM] Demurrage Impacted Shipments = 
CALCULATE(
    COUNTROWS(fact_customs_declarations),
    fact_customs_declarations[sim_demurrage_days] > 0
)

-- Documentation Discrepancy Rate %
[SIM] Doc Discrepancy Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_customs_declarations), fact_customs_declarations[sim_doc_discrepancy_flag] = 1),
    COUNTROWS(fact_customs_declarations),
    0
)

-- Red Channel Physical Cargo Inspection Hit Rate %
[SIM] Red Channel Inspection Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_customs_declarations), fact_customs_declarations[sim_inspection_channel] = "Red"),
    COUNTROWS(fact_customs_declarations),
    0
)

-- Yellow Channel Documentary Review Rate %
[SIM] Yellow Channel Review Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_customs_declarations), fact_customs_declarations[sim_inspection_channel] = "Yellow"),
    COUNTROWS(fact_customs_declarations),
    0
)

-- Estimated Customs Duties Paid (USD)
[SIM] Estimated Total Duties USD = 
SUM(fact_customs_declarations[sim_duty_amount_usd])
```
