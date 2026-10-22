# SQL Analytics: Query Execution & Results

Database: `data/supply_chain_analytics.db` (Star Schema)

## Query 1: Shipping Mode SLA Adherence & Average Delay Variance

```sql
-- ========================================================================
-- Supply Chain & International Trade Analytics: Analytical SQL Queries
-- Demonstrating Joins, Aggregations, CTEs, Window Functions, and Ranking
-- Database: supply_chain_dw (MySQL / SQLite Compatible)
-- Author: Antigravity & Senior Data Analyst Mentor
-- ========================================================================

-- ------------------------------------------------------------------------
-- QUERY 1: Shipping Mode SLA Adherence & Average Delay Variance
-- Business Question: Which shipping modes fail to meet scheduled transit SLAs,
-- and what is the realized delay distribution across modes?
-- Techniques: Multi-table JOIN, Conditional Aggregations (CASE WHEN), GROUP BY
-- ------------------------------------------------------------------------
SELECT 
    m.shipping_mode,
    COUNT(f.order_item_id) AS total_items_placed,
    SUM(CASE WHEN f.is_canceled = 0 THEN 1 ELSE 0 END) AS total_items_shipped,
    SUM(f.is_late) AS total_late_items,
    ROUND(SUM(f.is_on_time) * 100.0 / SUM(CASE WHEN f.is_canceled = 0 THEN 1 ELSE 0 END), 2) AS otd_rate_shipped_base_pct,
    ROUND(SUM(f.is_on_time) * 100.0 / COUNT(f.order_item_id), 2) AS otd_rate_total_placed_base_pct,
    ROUND(SUM(f.is_late) * 100.0 / COUNT(f.order_item_id), 2) AS late_delivery_rate_pct,
    ROUND(AVG(f.days_shipping_scheduled), 2) AS avg_scheduled_days,
    ROUND(AVG(f.days_shipping_real), 2) AS avg_real_days,
    ROUND(AVG(f.delay_days), 2) AS delay_variance_days,
    ROUND(AVG(CASE WHEN f.is_late = 1 THEN f.delay_days ELSE NULL END), 2) AS positive_late_delay_days,
    ROUND(SUM(f.sales_gross), 2) AS total_gross_sales_usd
FROM fact_shipments f
JOIN dim_shipping_mode m ON f.shipping_mode_id = m.shipping_mode_id
GROUP BY m.shipping_mode
ORDER BY late_delivery_rate_pct DESC
```

### Result (First 15 rows):

| shipping_mode   |   total_items_placed |   total_items_shipped |   total_late_items |   otd_rate_shipped_base_pct |   otd_rate_total_placed_base_pct |   late_delivery_rate_pct |   avg_scheduled_days |   avg_real_days |   delay_variance_days |   positive_late_delay_days |   total_gross_sales_usd |
|:----------------|---------------------:|----------------------:|-------------------:|----------------------------:|---------------------------------:|-------------------------:|---------------------:|----------------:|----------------------:|---------------------------:|------------------------:|
| First Class     |                27814 |                 26513 |              26513 |                        0    |                             0    |                    95.32 |                    1 |            2    |                  1    |                       1    |             5.67437e+06 |
| Second Class    |                35216 |                 33806 |              26987 |                       20.17 |                            19.36 |                    76.63 |                    2 |            3.99 |                  1.99 |                       2.5  |             7.14544e+06 |
| Same Day        |                 9737 |                  9293 |               4454 |                       52.07 |                            49.7  |                    45.74 |                    0 |            0.48 |                  0.48 |                       1    |             1.94253e+06 |
| Standard Class  |               107752 |                103153 |              41023 |                       60.23 |                            57.66 |                    38.07 |                    4 |            4    |                 -0    |                       1.51 |             2.20224e+07 |

## Query 2: Global Market Delivery Performance & Profitability

```sql
-- ------------------------------------------------------------------------
-- QUERY 2: Global Market Delivery Performance & Profitability
-- Business Question: How do global trade markets rank by fulfillment volume,
-- delivery delay rates, and profit margin ratio?
-- Techniques: CTE (Common Table Expressions), Multi-table Joins, Aggregation
-- ------------------------------------------------------------------------
WITH MarketMetrics AS (
    SELECT 
        d.order_market,
        COUNT(f.order_item_id) AS shipment_count,
        COUNT(DISTINCT f.order_id) AS order_count,
        SUM(f.is_late) AS late_count,
        SUM(f.sales_gross) AS total_sales,
        SUM(f.benefit_per_order) AS total_profit,
        AVG(f.delay_days) AS avg_delay
    FROM fact_shipments f
    JOIN dim_order_destination d ON f.destination_id = d.destination_id
    GROUP BY d.order_market
)
SELECT 
    order_market,
    shipment_count,
    order_count,
    ROUND(late_count * 100.0 / shipment_count, 2) AS late_rate_pct,
    ROUND(avg_delay, 2) AS avg_delay_days,
    ROUND(total_sales, 2) AS total_sales_usd,
    ROUND(total_profit, 2) AS total_profit_usd,
    ROUND(total_profit * 100.0 / total_sales, 2) AS net_profit_margin_pct
FROM MarketMetrics
ORDER BY shipment_count DESC
```

### Result (First 15 rows):

| order_market   |   shipment_count |   order_count |   late_rate_pct |   avg_delay_days |   total_sales_usd |   total_profit_usd |   net_profit_margin_pct |
|:---------------|-----------------:|--------------:|----------------:|-----------------:|------------------:|-------------------:|------------------------:|
| LATAM          |            51594 |         17181 |           54.36 |             0.56 |       1.02776e+07 |        1.12332e+06 |                   10.93 |
| Europe         |            50252 |         18561 |           55.21 |             0.57 |       1.08724e+07 |        1.16944e+06 |                   10.76 |
| Pacific Asia   |            41260 |         17577 |           55.05 |             0.57 |       8.27374e+06 |   857753           |                   10.37 |
| USCA           |            25799 |          8579 |           54.8  |             0.57 |       5.06653e+06 |   564314           |                   11.14 |
| Africa         |            11614 |          3854 |           54.59 |             0.56 |       2.29445e+06 |   252071           |                   10.99 |

## Query 3: Top Product Categories by Revenue and Delay Ranking (Window Functions)

```sql
-- ------------------------------------------------------------------------
-- QUERY 3: Category Revenue & Late Delivery Exposure Ranking
-- Business Question: What are the top product categories by revenue, and how 
-- do they rank in terms of customer delay exposure?
-- Techniques: CTE, Window Functions (DENSE_RANK), Partitioning
-- ------------------------------------------------------------------------
WITH CategorySummary AS (
    SELECT 
        p.category_name,
        p.department_name,
        COUNT(f.order_item_id) AS items_sold,
        SUM(f.sales_gross) AS gross_sales,
        SUM(f.benefit_per_order) AS net_profit,
        SUM(f.is_late) AS late_items
    FROM fact_shipments f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.category_name, p.department_name
)
SELECT 
    category_name,
    department_name,
    items_sold,
    ROUND(gross_sales, 2) AS gross_sales_usd,
    ROUND(net_profit, 2) AS net_profit_usd,
    ROUND(late_items * 100.0 / items_sold, 2) AS late_pct,
    DENSE_RANK() OVER (ORDER BY gross_sales DESC) AS revenue_rank,
    DENSE_RANK() OVER (ORDER BY (late_items * 100.0 / items_sold) DESC) AS late_rate_rank
FROM CategorySummary
ORDER BY revenue_rank ASC
LIMIT 15
```

### Result (First 15 rows):

| category_name        | department_name   |   items_sold |   gross_sales_usd |   net_profit_usd |   late_pct |   revenue_rank |   late_rate_rank |
|:---------------------|:------------------|-------------:|------------------:|-----------------:|-----------:|---------------:|-----------------:|
| Fishing              | Fan Shop          |        17325 |       6.92965e+06 |         756221   |      54.93 |              1 |               31 |
| Cleats               | Apparel           |        24551 |       4.43194e+06 |         494637   |      54.97 |              2 |               30 |
| Camping & Hiking     | Fan Shop          |        13729 |       4.11843e+06 |         427456   |      54.53 |              3 |               36 |
| Cardio Equipment     | Footwear          |        12487 |       3.69484e+06 |         383011   |      54.5  |              4 |               37 |
| Women's Apparel      | Golf              |        21035 |       3.1478e+06  |         350421   |      54.56 |              5 |               35 |
| Water Sports         | Fan Shop          |        15540 |       3.11384e+06 |         325147   |      54.81 |              6 |               32 |
| Men's Footwear       | Apparel           |        22246 |       2.89176e+06 |         311903   |      54.49 |              7 |               38 |
| Indoor/Outdoor Games | Fan Shop          |        19298 |       2.88899e+06 |         318451   |      54.75 |              8 |               33 |
| Shop By Sport        | Golf              |        10984 |       1.30952e+06 |         129814   |      55.15 |              9 |               28 |
| Computers            | Technology        |          442 |  663000           |          69656.8 |      50.68 |             10 |               50 |
| Cameras              | Technology        |          592 |  267608           |          30289.8 |      58.11 |             11 |                4 |
| Garden               | Outdoors          |          484 |  257769           |          33443   |      55.79 |             12 |               19 |
| Electronics          | Outdoors          |         2029 |  255679           |          28626.5 |      56.33 |             13 |               12 |
| Children's Clothing  | Apparel           |          652 |  232829           |          27178.1 |      53.37 |             14 |               46 |
| Crafts               | Apparel           |          484 |  223356           |          25531.2 |      55.99 |             15 |               16 |

## Query 4: Monthly Trajectory & 3-Month Moving Average (Window Functions)

```sql
-- ------------------------------------------------------------------------
-- QUERY 4: Monthly Trajectory & 3-Month Moving Average of Delay Variance
-- Business Question: Is delivery delay improving over time, and what is the 
-- cumulative volume trajectory across the 3-year timeline?
-- Techniques: Window Functions (SUM OVER, AVG OVER ROWS BETWEEN), Date Hierarchy
-- ------------------------------------------------------------------------
WITH MonthlyAggregates AS (
    SELECT 
        dt.year_month,
        dt.year,
        dt.month,
        COUNT(f.order_item_id) AS monthly_items,
        SUM(f.is_late) AS monthly_late_items,
        ROUND(AVG(f.delay_days), 3) AS monthly_avg_delay,
        SUM(f.sales_gross) AS monthly_sales
    FROM fact_shipments f
    JOIN dim_date dt ON f.order_date_key = dt.date_key
    GROUP BY dt.year_month, dt.year, dt.month
)
SELECT 
    year_month,
    monthly_items,
    ROUND(monthly_late_items * 100.0 / monthly_items, 2) AS monthly_late_pct,
    monthly_avg_delay,
    -- 3-Month Moving Average of Delay Days
    ROUND(AVG(monthly_avg_delay) OVER (
        ORDER BY year, month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 3) AS moving_avg_3m_delay,
    -- Cumulative Gross Sales across timeline
    ROUND(SUM(monthly_sales) OVER (
        ORDER BY year, month 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS cumulative_sales_usd
FROM MonthlyAggregates
ORDER BY year_month ASC
```

### Result (First 15 rows):

| year_month   |   monthly_items |   monthly_late_pct |   monthly_avg_delay |   moving_avg_3m_delay |   cumulative_sales_usd |
|:-------------|----------------:|-------------------:|--------------------:|----------------------:|-----------------------:|
| 2015-01      |            5322 |              54.11 |               0.54  |                 0.54  |            1.05159e+06 |
| 2015-02      |            4729 |              54.85 |               0.598 |                 0.569 |            1.9786e+06  |
| 2015-03      |            5362 |              54.76 |               0.572 |                 0.57  |            3.02985e+06 |
| 2015-04      |            5126 |              53.84 |               0.547 |                 0.572 |            4.04432e+06 |
| 2015-05      |            5357 |              55.09 |               0.557 |                 0.559 |            5.0948e+06  |
| 2015-06      |            5134 |              54.11 |               0.538 |                 0.547 |            6.1188e+06  |
| 2015-07      |            5299 |              55.46 |               0.573 |                 0.556 |            7.15688e+06 |
| 2015-08      |            5273 |              55.68 |               0.596 |                 0.569 |            8.18638e+06 |
| 2015-09      |            5140 |              56.69 |               0.582 |                 0.584 |            9.20472e+06 |
| 2015-10      |            5302 |              54.81 |               0.544 |                 0.574 |            1.02539e+07 |
| 2015-11      |            5235 |              54.27 |               0.562 |                 0.563 |            1.1283e+07  |
| 2015-12      |            5371 |              54.68 |               0.565 |                 0.557 |            1.23408e+07 |
| 2016-01      |            5317 |              55.58 |               0.596 |                 0.574 |            1.33871e+07 |
| 2016-02      |            4894 |              54.15 |               0.548 |                 0.57  |            1.43557e+07 |
| 2016-03      |            5210 |              55.76 |               0.558 |                 0.567 |            1.53815e+07 |

## Query 5: Order-Level Fulfillment Status Funnel

```sql
-- ------------------------------------------------------------------------
-- QUERY 5: Order-Level Exception & Fulfillment Funnel Analysis
-- Business Question: What proportion of customer orders face critical risk flags 
-- (Suspected Fraud, Canceled, Payment Review) vs standard fulfillment?
-- Techniques: Subquery aggregation, Percentage of Total, Conditional Summary
-- ------------------------------------------------------------------------
SELECT 
    order_status,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(order_item_id) AS total_items,
    ROUND(COUNT(order_item_id) * 100.0 / (SELECT COUNT(*) FROM fact_shipments), 2) AS pct_of_all_items,
    ROUND(SUM(sales_gross), 2) AS total_sales_exposure_usd,
    ROUND(AVG(days_shipping_real), 2) AS avg_fulfillment_days
FROM fact_shipments
GROUP BY order_status
ORDER BY total_items DESC
```

### Result (First 15 rows):

| order_status    |   distinct_orders |   total_items |   pct_of_all_items |   total_sales_exposure_usd |   avg_fulfillment_days |
|:----------------|------------------:|--------------:|-------------------:|---------------------------:|-----------------------:|
| COMPLETE        |             21716 |         59491 |              32.96 |                1.20953e+07 |                   3.49 |
| PENDING_PAYMENT |             14382 |         39832 |              22.07 |                8.1067e+06  |                   3.53 |
| PROCESSING      |              7901 |         21902 |              12.13 |                4.50406e+06 |                   3.49 |
| PENDING         |              7321 |         20227 |              11.2  |                4.12053e+06 |                   3.5  |
| CLOSED          |              7249 |         19616 |              10.87 |                4.02262e+06 |                   3.47 |
| ON_HOLD         |              3624 |          9804 |               5.43 |                1.98154e+06 |                   3.5  |
| SUSPECTED_FRAUD |              1488 |          4062 |               2.25 |           825935           |                   3.49 |
| CANCELED        |              1367 |          3692 |               2.05 |           744370           |                   3.46 |
| PAYMENT_REVIEW  |               704 |          1893 |               1.05 |           383654           |                   3.49 |

## Query 6: Relational Data Quality Exception Audit

```sql
-- ------------------------------------------------------------------------
-- QUERY 6: Data Quality Exception Audit (Sanity & Integrity Check)
-- Business Question: Are there any inverted timestamps, negative prices, or 
-- orphan records violating relational business rules?
-- Techniques: Exception Detection Query using UNION ALL
-- ------------------------------------------------------------------------
SELECT 
    'Inverted Timestamps (Shipping < Order)' AS check_name,
    COUNT(*) AS exception_count
FROM fact_shipments
WHERE shipping_timestamp < order_timestamp

UNION ALL

SELECT 
    'Negative or Zero Sales Values',
    COUNT(*)
FROM fact_shipments
WHERE sales_gross <= 0

UNION ALL

SELECT 
    'Negative Real Shipping Duration',
    COUNT(*)
FROM fact_shipments
WHERE days_shipping_real < 0

UNION ALL

SELECT 
    'Orphan Product Records (Unmatched FK)',
    COUNT(*)
FROM fact_shipments f
LEFT JOIN dim_product p ON f.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT 
    'Orphan Destination Records (Unmatched FK)',
    COUNT(*)
FROM fact_shipments f
LEFT JOIN dim_order_destination d ON f.destination_id = d.destination_id
WHERE d.destination_id IS NULL
```

### Result (First 15 rows):

| check_name                                |   exception_count |
|:------------------------------------------|------------------:|
| Inverted Timestamps (Shipping < Order)    |                 0 |
| Negative or Zero Sales Values             |                 0 |
| Negative Real Shipping Duration           |                 0 |
| Orphan Product Records (Unmatched FK)     |                 0 |
| Orphan Destination Records (Unmatched FK) |                 0 |

## Query 7: Cross-Border Trade Lane Demurrage & Modeled Freight Costs [SIMULATION]

```sql
-- ------------------------------------------------------------------------
-- QUERY 7: Cross-Border Trade Lane Customs Dwell & Modeled Freight Costs [SIMULATION]
-- Business Question: What is the average customs clearance dwell time, total 
-- demurrage penalty exposure, and modeled logistics freight cost across carrier partners?
-- Techniques: 1-to-1 Table Join (fact_shipments -> fact_customs_declarations), Aggregation
-- ------------------------------------------------------------------------
SELECT 
    c.sim_carrier_partner,
    COUNT(DISTINCT c.order_id) AS total_customs_declarations,
    ROUND(AVG(c.sim_dwell_time_days), 2) AS avg_customs_dwell_days,
    SUM(CASE WHEN c.sim_demurrage_days > 0 THEN 1 ELSE 0 END) AS demurrage_impacted_orders,
    ROUND(SUM(c.sim_demurrage_incurred_usd), 2) AS total_demurrage_incurred_usd,
    ROUND(SUM(c.sim_freight_cost_usd), 2) AS total_sim_freight_cost_usd,
    ROUND(AVG(c.sim_freight_cost_usd), 2) AS avg_freight_cost_per_order_usd,
    ROUND(SUM(c.sim_doc_discrepancy_flag) * 100.0 / COUNT(c.order_id), 2) AS doc_discrepancy_rate_pct
FROM fact_customs_declarations c
GROUP BY c.sim_carrier_partner
ORDER BY total_demurrage_incurred_usd DESC
```

### Result (First 15 rows):

| sim_carrier_partner         |   total_customs_declarations |   avg_customs_dwell_days |   demurrage_impacted_orders |   total_demurrage_incurred_usd |   total_sim_freight_cost_usd |   avg_freight_cost_per_order_usd |   doc_discrepancy_rate_pct |
|:----------------------------|-----------------------------:|-------------------------:|----------------------------:|-------------------------------:|-----------------------------:|---------------------------------:|---------------------------:|
| Maersk Line                 |                        13185 |                     1.7  |                        1764 |                         442617 |                  4.79318e+06 |                           363.53 |                       6.05 |
| CMA CGM Group               |                        13192 |                     1.69 |                        1707 |                         439582 |                  4.81011e+06 |                           364.62 |                       5.91 |
| Hapag-Lloyd Logistics       |                        13215 |                     1.68 |                        1675 |                         439333 |                  4.79447e+06 |                           362.81 |                       5.41 |
| MSC Mediterranean Shipping  |                        12922 |                     1.69 |                        1720 |                         439281 |                  4.71401e+06 |                           364.8  |                       5.73 |
| Ocean Network Express (ONE) |                        13238 |                     1.68 |                        1692 |                         429347 |                  4.82575e+06 |                           364.54 |                       5.84 |

