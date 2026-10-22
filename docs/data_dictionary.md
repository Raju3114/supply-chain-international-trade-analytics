# Master Data Dictionary

This data dictionary documents every field across the Core Supply Chain dataset and the Phase 2 Synthetic Customs Extension.

---

## 1. Lineage Classification Standard

* **`[ORIGINAL]`**: Authentic field from the raw DataCo dataset.
* **`[DERIVED]`**: Mathematically calculated from original fields in the data cleaning pipeline.
* **`[SIMULATED]`**: Generated companion record for the international trade extension (strictly prefixed with `sim_`).

---

## 2. Table: `fact_shipments` (Core Fact Table)
**Primary Grain:** 1 row per ordered item (`order_item_id`). Total Rows: `180,519`.

| Field Name | Lineage | Data Type | Nullable | Description & Domain Values |
| :--- | :--- | :--- | :--- | :--- |
| `order_item_id` | `[ORIGINAL]` | BIGINT (PK) | No | Unique surrogate key for each item within a customer order. |
| `order_id` | `[ORIGINAL]` | BIGINT | No | Transactional order identifier (65,752 distinct orders). |
| `order_date_key` | `[DERIVED]` | INT (FK) | No | Date key linking to `dim_date.date_key` (Format: `YYYYMMDD`). |
| `shipping_date_key` | `[DERIVED]` | INT (FK) | No | Date key linking to `dim_date.date_key` for fulfillment dispatch. |
| `order_timestamp` | `[ORIGINAL]` | DATETIME | No | Exact order placement timestamp (Range: 2015-01-01 to 2018-01-31). |
| `shipping_timestamp` | `[ORIGINAL]` | DATETIME | No | Exact dispatch timestamp (Range: 2015-01-03 to 2018-02-06). |
| `customer_id` | `[ORIGINAL]` | INT (FK) | No | Customer reference linking to `dim_customer_geo.customer_id`. |
| `product_id` | `[ORIGINAL]` | INT (FK) | No | Product reference linking to `dim_product.product_id`. |
| `shipping_mode_id` | `[ORIGINAL]` | INT (FK) | No | Shipping mode reference linking to `dim_shipping_mode.shipping_mode_id`. |
| `destination_id` | `[ORIGINAL]` | INT (FK) | No | Geographic destination reference linking to `dim_order_destination`. |
| `order_status` | `[ORIGINAL]` | VARCHAR(50)| No | Status: COMPLETE, PENDING_PAYMENT, PROCESSING, PENDING, CLOSED, ON_HOLD, SUSPECTED_FRAUD, CANCELED, PAYMENT_REVIEW. |
| `delivery_status` | `[ORIGINAL]` | VARCHAR(50)| No | Delivery outcome: Late delivery, Advance shipping, Shipping on time, Shipping canceled. |
| `days_shipping_real` | `[ORIGINAL]` | INT | No | Physical transit days realized (Range: 0 to 6 days). |
| `days_shipping_scheduled` | `[ORIGINAL]` | INT | No | Committed transit SLA in days (Range: 0 to 4 days). |
| `delay_days` | `[DERIVED]` | INT | No | `days_shipping_real - days_shipping_scheduled` (Positive = late, 0 = on-time, Negative = ahead). |
| `is_late` | `[DERIVED]` | TINYINT | No | 1 if `delivery_status == 'Late delivery'`, 0 otherwise. |
| `is_on_time` | `[DERIVED]` | TINYINT | No | 1 if delivered on or ahead of scheduled deadline, 0 otherwise. |
| `is_canceled` | `[DERIVED]` | TINYINT | No | 1 if `delivery_status == 'Shipping canceled'`, 0 otherwise. |
| `order_item_quantity` | `[ORIGINAL]` | INT | No | Quantity of units ordered for the item (Range: 1 to 5). |
| `product_price` | `[ORIGINAL]` | DECIMAL(10,2)| No | Unit price before discounts (Range: $9.99 to $1,999.99). |
| `order_item_discount` | `[ORIGINAL]` | DECIMAL(10,2)| No | Dollar value of discount applied. |
| `order_item_discount_rate` | `[ORIGINAL]` | DECIMAL(5,4)| No | Percentage discount (Range: 0.00 to 0.25). |
| `order_item_total` | `[ORIGINAL]` | DECIMAL(10,2)| No | Net billed amount after discount. |
| `sales_gross` | `[ORIGINAL]` | DECIMAL(10,2)| No | Gross sales value (`product_price * order_item_quantity`). |
| `order_item_profit_ratio` | `[ORIGINAL]` | DECIMAL(5,4)| No | Profit margin ratio per item (Range: -2.75 to 0.50). |
| `benefit_per_order` | `[ORIGINAL]` | DECIMAL(10,2)| No | Net operating profit/loss allocated to this order item. |

---

## 3. Table: `fact_customs_declarations` (Phase 2 Extension)
**Primary Grain:** 1 row per distinct order (`order_id`). Total Rows: `65,752`.

| Field Name | Lineage | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `sim_declaration_id` | `[SIMULATED]` | VARCHAR(50) PK | Deterministic Bill of Entry identifier (e.g., `DEC-2015-00000001`). |
| `order_id` | `[ORIGINAL FK]`| BIGINT | Foreign key matching `fact_shipments.order_id` (1:1 join). |
| `sim_trade_lane` | `[SIMULATED]` | VARCHAR(100) | Modeled trade lane (e.g. `EE. UU.-to-WesternEurope`). |
| `sim_carrier_partner`| `[SIMULATED]` | VARCHAR(100) | Modeled ocean/freight carrier: Maersk, MSC, CMA CGM, Hapag-Lloyd, ONE. |
| `sim_customs_broker` | `[SIMULATED]` | VARCHAR(100) | Licensed customs broker (Kuehne+Nagel, DHL, DB Schenker, Expeditors). |
| `sim_port_of_entry` | `[SIMULATED]` | VARCHAR(100) | International entry port (Rotterdam, Singapore, Antwerp, Santos, etc.). |
| `sim_hs_chapter` | `[SIMULATED]` | VARCHAR(10) | WCO Harmonized System 2-digit chapter (84, 85, 87). |
| `sim_hs_code` | `[SIMULATED]` | VARCHAR(20) | WCO Harmonized System 6-digit subheading (e.g., 8407.34, 8537.10, 8708.29). |
| `sim_port_arrival_timestamp` | `[SIMULATED]` | DATETIME | Vessel discharge timestamp at port of destination. |
| `sim_customs_release_timestamp` | `[SIMULATED]` | DATETIME | Customs out-of-charge / release timestamp. |
| `sim_dwell_time_days`| `[SIMULATED]` | DECIMAL(6,2) | Customs processing duration in calendar days. |
| `sim_inspection_channel` | `[SIMULATED]` | VARCHAR(20) | Risk routing: Green (Automated), Yellow (Doc Review), Red (Physical). |
| `sim_doc_discrepancy_flag` | `[SIMULATED]` | TINYINT | 1 if invoice or certificate error flagged, 0 otherwise. |
| `sim_free_days_limit`| `[SIMULATED]` | DECIMAL(4,1) | Standard free storage days allowed at terminal (3.0 days). |
| `sim_demurrage_days`| `[SIMULATED]` | DECIMAL(6,2) | Dwell days exceeding free time (`MAX(0, dwell - 3.0)`). |
| `sim_demurrage_incurred_usd` | `[SIMULATED]` | DECIMAL(10,2)| Demurrage penalty fee billed at $185/day. |
| `sim_duty_amount_usd` | `[SIMULATED]` | DECIMAL(10,2)| Modeled statutory tariff assessment based on HS chapter rate. |

---

## 4. Dimension Tables

### `dim_date`
* `date_key` (INT PK): `YYYYMMDD` (1,133 calendar days from 2015-01-01 to 2018-02-06).
* Attributes: `full_date`, `year`, `quarter`, `month`, `month_name`, `year_month`, `day_of_month`, `day_of_week`.

### `dim_product`
* `product_id` (INT PK): 118 distinct catalog items.
* Attributes: `product_name`, `category_id`, `category_name` (50 categories), `department_id`, `department_name` (11 departments).

### `dim_customer_geo`
* `customer_id` (INT PK): 20,652 distinct corporate and retail accounts.
* Attributes: `customer_fname`, `customer_lname`, `customer_segment` (*Consumer, Corporate, Home Office*), `customer_city`, `customer_state`, `customer_country`, `customer_zipcode`, `customer_latitude`, `customer_longitude`.

### `dim_shipping_mode`
* `shipping_mode_id` (INT PK): 1 (Standard Class), 2 (Second Class), 3 (First Class), 4 (Same Day).
* Attributes: `shipping_mode`, `standard_scheduled_days`.

### `dim_order_destination`
* `destination_id` (INT PK): 3,800 distinct geographical destination clusters.
* Attributes: `order_market` (Europe, LATAM, Pacific Asia, USCA, Africa), `order_region` (23 global regions), `order_country`, `order_state`, `order_city`, `order_zipcode`.
