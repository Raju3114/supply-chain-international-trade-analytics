"""
generate_pbip_model.py
----------------------
Generates the complete Tabular Model Definition (model.bim) and report layout (report.json)
for the Power BI Project (PBIP).

Author: Antigravity & Senior Data Analyst Mentor
"""

import json
import os

SEMANTIC_MODEL_PATH = os.path.join("power_bi", "Supply_Chain_Analytics.SemanticModel", "model.bim")
REPORT_LAYOUT_PATH = os.path.join("power_bi", "Supply_Chain_Analytics.Report", "report.json")

def generate_model_bim():
    # Model definition with standard MS Analysis Services schema
    model = {
        "name": "Supply_Chain_Analytics",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataSources": [
                {
                    "type": "structured",
                    "name": "ProcessedDataDirectory",
                    "connectionDetails": {
                        "protocol": "file",
                        "address": {
                            "path": "D:\\Projects\\Supply Chain & International\\data\\processed"
                        }
                    }
                }
            ],
            "tables": [
                {
                    "name": "fact_shipments",
                    "columns": [
                        {"name": "order_item_id", "dataType": "int64", "sourceColumn": "order_item_id"},
                        {"name": "order_id", "dataType": "int64", "sourceColumn": "order_id"},
                        {"name": "order_date_key", "dataType": "int64", "sourceColumn": "order_date_key"},
                        {"name": "shipping_date_key", "dataType": "int64", "sourceColumn": "shipping_date_key"},
                        {"name": "order_timestamp", "dataType": "dateTime", "sourceColumn": "order_timestamp"},
                        {"name": "shipping_timestamp", "dataType": "dateTime", "sourceColumn": "shipping_timestamp"},
                        {"name": "customer_id", "dataType": "int64", "sourceColumn": "customer_id"},
                        {"name": "product_id", "dataType": "int64", "sourceColumn": "product_id"},
                        {"name": "shipping_mode_id", "dataType": "int64", "sourceColumn": "shipping_mode_id"},
                        {"name": "destination_id", "dataType": "int64", "sourceColumn": "destination_id"},
                        {"name": "order_status", "dataType": "string", "sourceColumn": "order_status"},
                        {"name": "delivery_status", "dataType": "string", "sourceColumn": "delivery_status"},
                        {"name": "days_shipping_real", "dataType": "int64", "sourceColumn": "days_shipping_real"},
                        {"name": "days_shipping_scheduled", "dataType": "int64", "sourceColumn": "days_shipping_scheduled"},
                        {"name": "delay_days", "dataType": "int64", "sourceColumn": "delay_days"},
                        {"name": "is_late", "dataType": "int64", "sourceColumn": "is_late"},
                        {"name": "is_on_time", "dataType": "int64", "sourceColumn": "is_on_time"},
                        {"name": "is_canceled", "dataType": "int64", "sourceColumn": "is_canceled"},
                        {"name": "order_item_quantity", "dataType": "int64", "sourceColumn": "order_item_quantity"},
                        {"name": "product_price", "dataType": "double", "sourceColumn": "product_price", "formatString": "$#,##0.00"},
                        {"name": "order_item_discount", "dataType": "double", "sourceColumn": "order_item_discount", "formatString": "$#,##0.00"},
                        {"name": "order_item_discount_rate", "dataType": "double", "sourceColumn": "order_item_discount_rate", "formatString": "0.00%"},
                        {"name": "order_item_total", "dataType": "double", "sourceColumn": "order_item_total", "formatString": "$#,##0.00"},
                        {"name": "sales_gross", "dataType": "double", "sourceColumn": "sales_gross", "formatString": "$#,##0.00"},
                        {"name": "order_item_profit_ratio", "dataType": "double", "sourceColumn": "order_item_profit_ratio", "formatString": "0.00%"},
                        {"name": "benefit_per_order", "dataType": "double", "sourceColumn": "benefit_per_order", "formatString": "$#,##0.00"}
                    ],
                    "measures": [
                        {
                            "name": "Total Order Items",
                            "expression": "COUNTROWS(fact_shipments)",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Total Orders",
                            "expression": "DISTINCTCOUNT(fact_shipments[order_id])",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Total Gross Sales",
                            "expression": "SUM(fact_shipments[sales_gross])",
                            "formatString": "$#,##0.00"
                        },
                        {
                            "name": "Total Profit",
                            "expression": "SUM(fact_shipments[benefit_per_order])",
                            "formatString": "$#,##0.00"
                        },
                        {
                            "name": "Profit Margin %",
                            "expression": "DIVIDE([Total Profit], [Total Gross Sales], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Late Deliveries",
                            "expression": "CALCULATE(COUNTROWS(fact_shipments), fact_shipments[is_late] = 1)",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "On-Time Deliveries",
                            "expression": "CALCULATE(COUNTROWS(fact_shipments), fact_shipments[is_on_time] = 1)",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "On-Time Delivery Rate %",
                            "expression": "DIVIDE([On-Time Deliveries], [Total Order Items], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Late Delivery Rate %",
                            "expression": "DIVIDE([Late Deliveries], [Total Order Items], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Avg Delay Days",
                            "expression": "CALCULATE(AVERAGE(fact_shipments[delay_days]), fact_shipments[is_late] = 1)",
                            "formatString": "0.00"
                        }
                    ]
                },
                {
                    "name": "fact_customs_declarations",
                    "columns": [
                        {"name": "sim_declaration_id", "dataType": "string", "sourceColumn": "sim_declaration_id"},
                        {"name": "order_id", "dataType": "int64", "sourceColumn": "order_id"},
                        {"name": "sim_trade_lane", "dataType": "string", "sourceColumn": "sim_trade_lane"},
                        {"name": "sim_carrier_partner", "dataType": "string", "sourceColumn": "sim_carrier_partner"},
                        {"name": "sim_customs_broker", "dataType": "string", "sourceColumn": "sim_customs_broker"},
                        {"name": "sim_port_of_entry", "dataType": "string", "sourceColumn": "sim_port_of_entry"},
                        {"name": "sim_hs_chapter", "dataType": "string", "sourceColumn": "sim_hs_chapter"},
                        {"name": "sim_hs_code", "dataType": "string", "sourceColumn": "sim_hs_code"},
                        {"name": "sim_port_arrival_timestamp", "dataType": "dateTime", "sourceColumn": "sim_port_arrival_timestamp"},
                        {"name": "sim_customs_release_timestamp", "dataType": "dateTime", "sourceColumn": "sim_customs_release_timestamp"},
                        {"name": "sim_dwell_time_days", "dataType": "double", "sourceColumn": "sim_dwell_time_days", "formatString": "0.00"},
                        {"name": "sim_inspection_channel", "dataType": "string", "sourceColumn": "sim_inspection_channel"},
                        {"name": "sim_doc_discrepancy_flag", "dataType": "int64", "sourceColumn": "sim_doc_discrepancy_flag"},
                        {"name": "sim_free_days_limit", "dataType": "double", "sourceColumn": "sim_free_days_limit"},
                        {"name": "sim_demurrage_days", "dataType": "double", "sourceColumn": "sim_demurrage_days"},
                        {"name": "sim_demurrage_incurred_usd", "dataType": "double", "sourceColumn": "sim_demurrage_incurred_usd", "formatString": "$#,##0.00"},
                        {"name": "sim_duty_amount_usd", "dataType": "double", "sourceColumn": "sim_duty_amount_usd", "formatString": "$#,##0.00"}
                    ],
                    "measures": [
                        {
                            "name": "[SIM] Avg Customs Dwell Days",
                            "expression": "AVERAGE(fact_customs_declarations[sim_dwell_time_days])",
                            "formatString": "0.00"
                        },
                        {
                            "name": "[SIM] Total Demurrage USD",
                            "expression": "SUM(fact_customs_declarations[sim_demurrage_incurred_usd])",
                            "formatString": "$#,##0.00"
                        },
                        {
                            "name": "[SIM] Doc Discrepancy Rate %",
                            "expression": "DIVIDE(CALCULATE(COUNTROWS(fact_customs_declarations), fact_customs_declarations[sim_doc_discrepancy_flag] = 1), COUNTROWS(fact_customs_declarations), 0)",
                            "formatString": "0.00%"
                        }
                    ]
                },
                {
                    "name": "dim_date",
                    "columns": [
                        {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key"},
                        {"name": "full_date", "dataType": "dateTime", "sourceColumn": "full_date"},
                        {"name": "year", "dataType": "int64", "sourceColumn": "year"},
                        {"name": "quarter", "dataType": "string", "sourceColumn": "quarter"},
                        {"name": "month", "dataType": "int64", "sourceColumn": "month"},
                        {"name": "month_name", "dataType": "string", "sourceColumn": "month_name"},
                        {"name": "year_month", "dataType": "string", "sourceColumn": "year_month"},
                        {"name": "day_of_month", "dataType": "int64", "sourceColumn": "day_of_month"},
                        {"name": "day_of_week", "dataType": "string", "sourceColumn": "day_of_week"}
                    ]
                },
                {
                    "name": "dim_product",
                    "columns": [
                        {"name": "product_id", "dataType": "int64", "sourceColumn": "product_id"},
                        {"name": "product_name", "dataType": "string", "sourceColumn": "product_name"},
                        {"name": "category_id", "dataType": "int64", "sourceColumn": "category_id"},
                        {"name": "category_name", "dataType": "string", "sourceColumn": "category_name"},
                        {"name": "department_id", "dataType": "int64", "sourceColumn": "department_id"},
                        {"name": "department_name", "dataType": "string", "sourceColumn": "department_name"}
                    ]
                },
                {
                    "name": "dim_shipping_mode",
                    "columns": [
                        {"name": "shipping_mode_id", "dataType": "int64", "sourceColumn": "shipping_mode_id"},
                        {"name": "shipping_mode", "dataType": "string", "sourceColumn": "shipping_mode"},
                        {"name": "standard_scheduled_days", "dataType": "int64", "sourceColumn": "standard_scheduled_days"}
                    ]
                },
                {
                    "name": "dim_customer_geo",
                    "columns": [
                        {"name": "customer_id", "dataType": "int64", "sourceColumn": "customer_id"},
                        {"name": "customer_fname", "dataType": "string", "sourceColumn": "customer_fname"},
                        {"name": "customer_lname", "dataType": "string", "sourceColumn": "customer_lname"},
                        {"name": "customer_segment", "dataType": "string", "sourceColumn": "customer_segment"},
                        {"name": "customer_city", "dataType": "string", "sourceColumn": "customer_city"},
                        {"name": "customer_state", "dataType": "string", "sourceColumn": "customer_state"},
                        {"name": "customer_country", "dataType": "string", "sourceColumn": "customer_country"}
                    ]
                },
                {
                    "name": "dim_order_destination",
                    "columns": [
                        {"name": "destination_id", "dataType": "int64", "sourceColumn": "destination_id"},
                        {"name": "order_market", "dataType": "string", "sourceColumn": "order_market"},
                        {"name": "order_region", "dataType": "string", "sourceColumn": "order_region"},
                        {"name": "order_country", "dataType": "string", "sourceColumn": "order_country"},
                        {"name": "order_city", "dataType": "string", "sourceColumn": "order_city"}
                    ]
                }
            ],
            "relationships": [
                {
                    "name": "fact_shipments_order_date",
                    "fromTable": "fact_shipments",
                    "fromColumn": "order_date_key",
                    "toTable": "dim_date",
                    "toColumn": "date_key"
                },
                {
                    "name": "fact_shipments_product",
                    "fromTable": "fact_shipments",
                    "fromColumn": "product_id",
                    "toTable": "dim_product",
                    "toColumn": "product_id"
                },
                {
                    "name": "fact_shipments_shipping_mode",
                    "fromTable": "fact_shipments",
                    "fromColumn": "shipping_mode_id",
                    "toTable": "dim_shipping_mode",
                    "toColumn": "shipping_mode_id"
                },
                {
                    "name": "fact_shipments_customer",
                    "fromTable": "fact_shipments",
                    "fromColumn": "customer_id",
                    "toTable": "dim_customer_geo",
                    "toColumn": "customer_id"
                },
                {
                    "name": "fact_shipments_destination",
                    "fromTable": "fact_shipments",
                    "fromColumn": "destination_id",
                    "toTable": "dim_order_destination",
                    "toColumn": "destination_id"
                },
                {
                    "name": "fact_shipments_customs_declarations",
                    "fromTable": "fact_shipments",
                    "fromColumn": "order_id",
                    "toTable": "fact_customs_declarations",
                    "toColumn": "order_id",
                    "crossFilteringBehavior": "bothDirections"
                }
            ]
        }
    }

    with open(SEMANTIC_MODEL_PATH, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)
    print(f"Saved Tabular Semantic Model definition to {SEMANTIC_MODEL_PATH}")

def generate_report_json():
    # Report layout defining 5 interactive pages with cards, charts, and slicers
    report = {
        "version": "1.0",
        "theme": "ExecutiveDarkBlue",
        "sections": [
            {
                "name": "ExecutiveOverview",
                "displayName": "Executive Overview",
                "ordinal": 0,
                "visualContainers": [
                    {"type": "card", "title": "Total Gross Sales", "measure": "[Total Gross Sales]", "x": 20, "y": 20, "width": 220, "height": 110},
                    {"type": "card", "title": "Total Items Shipped", "measure": "[Total Order Items]", "x": 260, "y": 20, "width": 220, "height": 110},
                    {"type": "card", "title": "On-Time Delivery Rate", "measure": "[On-Time Delivery Rate %]", "x": 500, "y": 20, "width": 220, "height": 110},
                    {"type": "card", "title": "Late Delivery Rate", "measure": "[Late Delivery Rate %]", "x": 740, "y": 20, "width": 220, "height": 110},
                    {"type": "card", "title": "Operating Profit", "measure": "[Total Profit]", "x": 980, "y": 20, "width": 220, "height": 110},
                    {"type": "lineChart", "title": "Monthly Shipment Volume & Sales Trend", "x": 20, "y": 150, "width": 700, "height": 380},
                    {"type": "barChart", "title": "Sales & Late Rate by Destination Market", "x": 740, "y": 150, "width": 460, "height": 380}
                ]
            },
            {
                "name": "DeliveryPerformance",
                "displayName": "Delivery Performance",
                "ordinal": 1,
                "visualContainers": [
                    {"type": "barChart", "title": "Scheduled SLA vs Actual Realized Transit Duration", "x": 20, "y": 20, "width": 600, "height": 450},
                    {"type": "columnChart", "title": "Late Delivery Rate % by Shipping Mode", "x": 640, "y": 20, "width": 560, "height": 450}
                ]
            },
            {
                "name": "RegionalLogistics",
                "displayName": "Regional Logistics",
                "ordinal": 2,
                "visualContainers": [
                    {"type": "matrix", "title": "Global Market & Region Order Volume vs On-Time Performance", "x": 20, "y": 20, "width": 1180, "height": 550}
                ]
            },
            {
                "name": "ProductPortfolio",
                "displayName": "Product Portfolio",
                "ordinal": 3,
                "visualContainers": [
                    {"type": "barChart", "title": "Top 15 Revenue Categories vs Late Delivery Exposure", "x": 20, "y": 20, "width": 1180, "height": 550}
                ]
            },
            {
                "name": "InternationalCustoms",
                "displayName": "Customs & Trade [SIMULATED]",
                "ordinal": 4,
                "visualContainers": [
                    {"type": "card", "title": "Avg Customs Dwell (Days)", "measure": "[SIM] Avg Customs Dwell Days", "x": 20, "y": 20, "width": 280, "height": 110},
                    {"type": "card", "title": "Total Demurrage Exposure", "measure": "[SIM] Total Demurrage USD", "x": 320, "y": 20, "width": 280, "height": 110},
                    {"type": "card", "title": "Doc Discrepancy Rate", "measure": "[SIM] Doc Discrepancy Rate %", "x": 620, "y": 20, "width": 280, "height": 110},
                    {"type": "barChart", "title": "Average Dwell Time by Inspection Channel (Green, Yellow, Red)", "x": 20, "y": 150, "width": 580, "height": 400},
                    {"type": "barChart", "title": "Demurrage Incurred by Port of Entry", "x": 620, "y": 150, "width": 580, "height": 400}
                ]
            }
        ]
    }

    with open(REPORT_LAYOUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved Power BI Report layout to {REPORT_LAYOUT_PATH}")

if __name__ == "__main__":
    generate_model_bim()
    generate_report_json()
