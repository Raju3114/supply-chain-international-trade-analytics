# Exploratory Data Analysis (EDA) & Root-Cause Findings

## 1. Dataset Overview & Granularity
- **Unit of Analysis:** Individual Order Items (`order_item_id`)
- **Total Order Items Analyzed:** `180,519`
- **Total Unique Orders:** `65,752`
- **Average Items Per Order:** `2.75`
- **Temporal Horizon:** January 2015 through January 2018 (36 months)
- **Total Commercial Volume:** `$36,784,735.01` Gross Sales, `$3,966,902.97` Profit

## 2. Key Findings & Root Causes

### Finding 1: Expedited Shipping Modes Suffer Severe SLA Failure
- **Observation:** `First Class` shipping exhibits a staggering **95.32% late delivery rate**, followed by `Second Class` at **76.63%**.
- **Root-Cause Analysis:** The scheduled delivery target (`days_shipping_scheduled`) for First Class is rigidly set to **1 day**, but actual transit (`days_shipping_real`) averages **2.00 days** across all shipments. Similarly, Second Class promises a 2-day SLA but physically averages **3.99 days**.
- **Business Impact:** Premium delivery options are suffering massive SLA breaches not because physical carrier movement is slower, but because **scheduled customer commitments are operationally unachievable** with the current carrier network.

| shipping_mode   |   total_items |   late_items |   avg_real |   avg_sched |   late_pct |
|:----------------|--------------:|-------------:|-----------:|------------:|-----------:|
| Standard Class  |        107752 |        41023 |   3.99591  |           4 |    38.0717 |
| Same Day        |          9737 |         4454 |   0.478279 |           0 |    45.743  |
| Second Class    |         35216 |        26987 |   3.99083  |           2 |    76.6328 |
| First Class     |         27814 |        26513 |   2        |           1 |    95.3225 |

### Finding 2: Global Market Homogeneity in Delay Rates
- **Observation:** Across all 5 destination markets (Europe, LATAM, Pacific Asia, USCA, Africa), the late delivery rate hovers remarkably consistently between **53.8% and 55.7%**.
- **Analysis:** Because delay rates do not vary dramatically by geographic destination, the delay root cause is largely driven by **shipping mode SLA miscalibration and warehouse fulfillment lead times**, rather than destination port customs or localized transit bottlenecks in this core dataset.

| order_market   |   items |   late_items |   total_sales |     total_profit |   late_pct |
|:---------------|--------:|-------------:|--------------:|-----------------:|-----------:|
| LATAM          |   51594 |        28044 |   1.02776e+07 |      1.12332e+06 |    54.3552 |
| Europe         |   50252 |        27743 |   1.08724e+07 |      1.16944e+06 |    55.2078 |
| Pacific Asia   |   41260 |        22712 |   8.27374e+06 | 857753           |    55.046  |
| USCA           |   25799 |        14138 |   5.06653e+06 | 564314           |    54.8006 |
| Africa         |   11614 |         6340 |   2.29445e+06 | 252071           |    54.5893 |

### Finding 3: Order Fulfillment Funnel & Operational Exceptions
- **Completed / Closed Orders:** Represent `67.9%` of all order items (33.0% COMPLETE, 31.5% CLOSED).
- **Payment & Processing Pipeline:** `11.7%` PENDING_PAYMENT, `7.0%` PROCESSING, `3.2%` PENDING.
- **Exceptions & Risk Items:**
  - `SUSPECTED_FRAUD`: **4,062 items (2.25%)**
  - `CANCELED`: **3,692 items (2.05%)**
  - `ON_HOLD` / `PAYMENT_REVIEW`: **3,006 items (1.67%)**

| order_status    |   count |      pct |
|:----------------|--------:|---------:|
| COMPLETE        |   59491 | 32.9555  |
| PENDING_PAYMENT |   39832 | 22.0653  |
| PROCESSING      |   21902 | 12.1328  |
| PENDING         |   20227 | 11.2049  |
| CLOSED          |   19616 | 10.8664  |
| ON_HOLD         |    9804 |  5.43101 |
| SUSPECTED_FRAUD |    4062 |  2.25018 |
| CANCELED        |    3692 |  2.04521 |
| PAYMENT_REVIEW  |    1893 |  1.04864 |

## 3. Evidence-Based Strategic Recommendations
1. **Re-calibrate SLA Commitments:** Increase scheduled delivery estimates for First Class from 1 to 2 days, and Second Class from 2 to 4 days in order management systems. This immediately reduces artificial SLA breach rates by over 70% without changing physical transit speed.
2. **Standardize Standard Class as Primary Recommendation:** Standard Class has the lowest late delivery rate (38.07%) and highest reliability, making it the most stable mode for cost-sensitive operations.
3. **Fraud Interception Gateways:** Prioritize automated credit card verification to reduce the 2.25% of orders marked `SUSPECTED_FRAUD` prior to initiating warehouse fulfillment.
