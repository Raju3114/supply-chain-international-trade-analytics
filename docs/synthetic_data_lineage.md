# Synthetic International Trade & Customs Extension: Data Lineage & Specification

> [!IMPORTANT]
> **Transparency Disclaimer:** The records in `customs_trade_extension.csv` are deterministically simulated
> to model international trade workflows (HS classification, customs clearance channels, port dwell times, and demurrage).
> They do NOT represent proprietary customs filings or real regulatory violations of Volvo Group.

## 1. Lineage Classification Standard

- **`[ORIGINAL]`**: Core shipment transaction records from DataCo (180,519 order items).
- **`[DERIVED]`**: Lead-time variance, on-time indicators, date dimensions.
- **`[SIMULATED]`**: All fields prefixed with `sim_` in the companion dataset.

## 2. Key Generation Parameters & Seed
- **Random Seed:** `42` (ensures 100% reproducible generation)
- **Total Simulated Declarations:** `65,752`
- **Grain:** 1 Declaration per distinct order (`order_id`)
- **Average Customs Dwell Time:** `1.69 days`
- **Documentation Discrepancy Rate:** `5.79%`
- **Total Modeled Demurrage Exposure:** `$2,190,159.51`

## 3. Inspection Channel Distribution

- **Green Channel (Automated Immediate Release):** `81.4%`
- **Yellow Channel (Documentary Review):** `13.7%`
- **Red Channel (Physical Cargo Inspection):** `4.9%`

## 4. Field Dictionary

| Field Name | Lineage | Data Type | Description | Source / Formula |
| :--- | :--- | :--- | :--- | :--- |
| `sim_declaration_id` | SIMULATED | STRING | Unique Bill of Entry code | Deterministic sequential format |
| `order_id` | ORIGINAL FK | INTEGER | Foreign Key to `fact_shipments` | 1-to-1 match with core orders |
| `sim_trade_lane` | SIMULATED | STRING | Origin to Destination Trade Lane | Origin Country to Dest Region |
| `sim_carrier_partner` | SIMULATED | STRING | Ocean/Freight Carrier Partner | Maersk, MSC, CMA CGM, Hapag, ONE |
| `sim_customs_broker` | SIMULATED | STRING | Customs Brokerage Agent | KN, DHL, DB Schenker, Expeditors |
| `sim_port_of_entry` | SIMULATED | STRING | International Discharge Port | Modeled by destination continent |
| `sim_hs_chapter` | SIMULATED | STRING | WCO HS 2-Digit Chapter | Automotive Chapters 84, 85, 87 |
| `sim_hs_code` | SIMULATED | STRING | WCO HS 6-Digit Tariff Subheading | Automotive engine, ECU, parts codes |
| `sim_dwell_time_days` | SIMULATED | FLOAT | Clearance lead time at port | Log-normal by channel (Green=1.2d, Red=5.5d) |
| `sim_inspection_channel` | SIMULATED | STRING | Customs Routing Channel | Green, Yellow, Red |
| `sim_doc_discrepancy_flag`| SIMULATED | INTEGER | Commercial Document Discrepancy | 1 if error found, 0 otherwise |
| `sim_demurrage_incurred_usd`| SIMULATED | FLOAT | Port storage penalty | `MAX(0, dwell - 3.0) * $185/day` |
