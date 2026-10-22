-- ========================================================================
-- Supply Chain & International Trade Analytics: SQLite DDL
-- Star Schema Dimensional Model (Self-Contained Local Execution Engine)
-- Author: Antigravity & Senior Data Analyst Mentor
-- ========================================================================

PRAGMA foreign_keys = ON;

-- 1. Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    year_month TEXT NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week TEXT NOT NULL
);

-- 2. Product Dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    department_name TEXT NOT NULL
);

-- 3. Customer Dimension
CREATE TABLE IF NOT EXISTS dim_customer_geo (
    customer_id INTEGER PRIMARY KEY,
    customer_fname TEXT NOT NULL,
    customer_lname TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    customer_city TEXT NOT NULL,
    customer_state TEXT NOT NULL,
    customer_country TEXT NOT NULL,
    customer_zipcode TEXT NOT NULL,
    customer_latitude REAL,
    customer_longitude REAL
);

-- 4. Shipping Mode Dimension
CREATE TABLE IF NOT EXISTS dim_shipping_mode (
    shipping_mode_id INTEGER PRIMARY KEY,
    shipping_mode TEXT NOT NULL UNIQUE,
    standard_scheduled_days INTEGER NOT NULL
);

-- 5. Order Destination Dimension
CREATE TABLE IF NOT EXISTS dim_order_destination (
    destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_market TEXT NOT NULL,
    order_region TEXT NOT NULL,
    order_country TEXT NOT NULL,
    order_state TEXT NOT NULL,
    order_city TEXT NOT NULL,
    order_zipcode TEXT NOT NULL
);

-- 6. Fact Shipments Table
CREATE TABLE IF NOT EXISTS fact_shipments (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    order_date_key INTEGER NOT NULL,
    shipping_date_key INTEGER NOT NULL,
    order_timestamp TEXT NOT NULL,
    shipping_timestamp TEXT NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    shipping_mode_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    order_status TEXT NOT NULL,
    delivery_status TEXT NOT NULL,
    days_shipping_real INTEGER NOT NULL,
    days_shipping_scheduled INTEGER NOT NULL,
    delay_days INTEGER NOT NULL,
    is_late INTEGER NOT NULL,
    is_on_time INTEGER NOT NULL,
    is_canceled INTEGER NOT NULL,
    order_item_quantity INTEGER NOT NULL,
    product_price REAL NOT NULL,
    order_item_discount REAL NOT NULL,
    order_item_discount_rate REAL NOT NULL,
    order_item_total REAL NOT NULL,
    sales_gross REAL NOT NULL,
    order_item_profit_ratio REAL NOT NULL,
    benefit_per_order REAL NOT NULL,
    
    FOREIGN KEY (order_date_key) REFERENCES dim_date (date_key),
    FOREIGN KEY (shipping_date_key) REFERENCES dim_date (date_key),
    FOREIGN KEY (customer_id) REFERENCES dim_customer_geo (customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
    FOREIGN KEY (shipping_mode_id) REFERENCES dim_shipping_mode (shipping_mode_id),
    FOREIGN KEY (destination_id) REFERENCES dim_order_destination (destination_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_order_id ON fact_shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_delivery_status ON fact_shipments(delivery_status);
CREATE INDEX IF NOT EXISTS idx_fact_is_late ON fact_shipments(is_late);
CREATE INDEX IF NOT EXISTS idx_fact_order_timestamp ON fact_shipments(order_timestamp);
