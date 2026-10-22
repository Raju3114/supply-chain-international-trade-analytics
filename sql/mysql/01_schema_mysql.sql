-- ========================================================================
-- Supply Chain & International Trade Analytics: MySQL 8.0 DDL
-- Star Schema Dimensional Model
-- Author: Antigravity & Senior Data Analyst Mentor
-- ========================================================================

DROP DATABASE IF EXISTS supply_chain_dw;
CREATE DATABASE supply_chain_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE supply_chain_dw;

-- 1. Date Dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,                 -- YYYYMMDD
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter VARCHAR(10) NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    day_of_month INT NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    INDEX idx_year_month (year_month)
) ENGINE=InnoDB;

-- 2. Product Dimension
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    INDEX idx_category (category_name),
    INDEX idx_department (department_name)
) ENGINE=InnoDB;

-- 3. Customer Dimension
CREATE TABLE dim_customer_geo (
    customer_id INT PRIMARY KEY,
    customer_fname VARCHAR(100) NOT NULL,
    customer_lname VARCHAR(100) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state VARCHAR(100) NOT NULL,
    customer_country VARCHAR(100) NOT NULL,
    customer_zipcode VARCHAR(20) NOT NULL,
    customer_latitude DECIMAL(10, 6),
    customer_longitude DECIMAL(10, 6),
    INDEX idx_customer_segment (customer_segment),
    INDEX idx_customer_country (customer_country)
) ENGINE=InnoDB;

-- 4. Shipping Mode Dimension
CREATE TABLE dim_shipping_mode (
    shipping_mode_id INT PRIMARY KEY,
    shipping_mode VARCHAR(50) NOT NULL UNIQUE,
    standard_scheduled_days INT NOT NULL
) ENGINE=InnoDB;

-- 5. Order Destination Dimension
CREATE TABLE dim_order_destination (
    destination_id INT AUTO_INCREMENT PRIMARY KEY,
    order_market VARCHAR(50) NOT NULL,
    order_region VARCHAR(100) NOT NULL,
    order_country VARCHAR(100) NOT NULL,
    order_state VARCHAR(100) NOT NULL,
    order_city VARCHAR(100) NOT NULL,
    order_zipcode VARCHAR(20) NOT NULL,
    UNIQUE KEY uk_geo (order_market, order_region, order_country, order_state, order_city, order_zipcode),
    INDEX idx_market_region (order_market, order_region)
) ENGINE=InnoDB;

-- 6. Core Fact Table: Fact Shipments (Grain: 1 row per order item)
CREATE TABLE fact_shipments (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    order_date_key INT NOT NULL,
    shipping_date_key INT NOT NULL,
    order_timestamp DATETIME NOT NULL,
    shipping_timestamp DATETIME NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    shipping_mode_id INT NOT NULL,
    destination_id INT NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    delivery_status VARCHAR(50) NOT NULL,
    days_shipping_real INT NOT NULL,
    days_shipping_scheduled INT NOT NULL,
    delay_days INT NOT NULL,
    is_late TINYINT NOT NULL,
    is_on_time TINYINT NOT NULL,
    is_canceled TINYINT NOT NULL,
    order_item_quantity INT NOT NULL,
    product_price DECIMAL(10, 2) NOT NULL,
    order_item_discount DECIMAL(10, 2) NOT NULL,
    order_item_discount_rate DECIMAL(6, 4) NOT NULL,
    order_item_total DECIMAL(10, 2) NOT NULL,
    sales_gross DECIMAL(10, 2) NOT NULL,
    order_item_profit_ratio DECIMAL(6, 4) NOT NULL,
    benefit_per_order DECIMAL(10, 2) NOT NULL,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_shipments_order_date FOREIGN KEY (order_date_key) REFERENCES dim_date (date_key),
    CONSTRAINT fk_shipments_shipping_date FOREIGN KEY (shipping_date_key) REFERENCES dim_date (date_key),
    CONSTRAINT fk_shipments_customer FOREIGN KEY (customer_id) REFERENCES dim_customer_geo (customer_id),
    CONSTRAINT fk_shipments_product FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
    CONSTRAINT fk_shipments_mode FOREIGN KEY (shipping_mode_id) REFERENCES dim_shipping_mode (shipping_mode_id),
    CONSTRAINT fk_shipments_dest FOREIGN KEY (destination_id) REFERENCES dim_order_destination (destination_id),
    
    INDEX idx_order_id (order_id),
    INDEX idx_delivery_status (delivery_status),
    INDEX idx_is_late (is_late),
    INDEX idx_order_timestamp (order_timestamp)
) ENGINE=InnoDB;
