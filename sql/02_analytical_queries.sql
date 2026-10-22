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
ORDER BY late_delivery_rate_pct DESC;


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
ORDER BY shipment_count DESC;


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
LIMIT 15;


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
ORDER BY year_month ASC;


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
ORDER BY total_items DESC;


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
WHERE d.destination_id IS NULL;


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
ORDER BY total_demurrage_incurred_usd DESC;

