// Power Query M Script for Power BI Desktop
// Copy-paste this script into Power BI's Advanced Editor or Blank Query to import clean_shipments.csv
let
    // Update path if repository is moved
    Source = Csv.Document(File.Contents("D:\Projects\Supply Chain & International\data\processed\clean_shipments.csv"),[Delimiter=",", Columns=37, Encoding=1252, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"order_date", type datetime},
        {"shipping_date", type datetime},
        {"days_shipping_real", Int64.Type},
        {"days_shipping_scheduled", Int64.Type},
        {"late_delivery_risk", Int64.Type},
        {"order_item_id", Int64.Type},
        {"order_id", Int64.Type},
        {"order_item_quantity", Int64.Type},
        {"product_price", type number},
        {"order_item_discount", type number},
        {"order_item_discount_rate", type number},
        {"order_item_total", type number},
        {"sales_gross", type number},
        {"order_item_profit_ratio", type number},
        {"benefit_per_order", type number},
        {"customer_id", Int64.Type},
        {"product_id", Int64.Type},
        {"category_id", Int64.Type},
        {"department_id", Int64.Type},
        {"delay_days", Int64.Type},
        {"is_late", Int64.Type},
        {"is_on_time", Int64.Type},
        {"is_canceled", Int64.Type},
        {"order_year", Int64.Type},
        {"order_month_num", Int64.Type}
    })
in
    #"Changed Type"
