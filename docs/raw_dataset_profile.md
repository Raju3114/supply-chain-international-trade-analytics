# Raw Dataset Profile: DataCo Smart Supply Chain

- **Source File:** `data/raw/DataCoSupplyChainDataset.csv`
- **Encoding:** `latin-1`
- **Total Rows:** 180,519
- **Total Columns:** 53
- **Unique Order Items (Primary Grain):** 180,519
- **Unique Orders:** 65,752
- **Full Row Duplicates:** 0

## Delivery & Shipping Sanity Checks
- `Days for shipping (real)` Range: `0` to `6` days (Mean: 3.50)
- `Days for shipment (scheduled)` Range: `0` to `4` days (Mean: 2.93)
- Negative Real Shipping Days: `0`
- Negative Scheduled Shipping Days: `0`

## Missing Values Summary

| Column              | Dtype   |   Missing |   Pct_Missing |   Unique_Values | Sample   |
|:--------------------|:--------|----------:|--------------:|----------------:|:---------|
| Customer Lname      | str     |         8 |          0    |            1109 | Holloway |
| Customer Zipcode    | float64 |         3 |          0    |             995 | 725.0    |
| Order Zipcode       | float64 |    155679 |         86.24 |             609 | 99301.0  |
| Product Description | float64 |    180519 |        100    |               0 | N/A      |

## Full Column Schema & Profiling

| Column                        | Dtype   |   Missing |   Pct_Missing |   Unique_Values | Sample                         |
|:------------------------------|:--------|----------:|--------------:|----------------:|:-------------------------------|
| Type                          | str     |         0 |          0    |               4 | DEBIT                          |
| Days for shipping (real)      | int64   |         0 |          0    |               7 | 3                              |
| Days for shipment (scheduled) | int64   |         0 |          0    |               4 | 4                              |
| Benefit per order             | float64 |         0 |          0    |           21998 | 91.25                          |
| Sales per customer            | float64 |         0 |          0    |            2927 | 314.6400146                    |
| Delivery Status               | str     |         0 |          0    |               4 | Advance shipping               |
| Late_delivery_risk            | int64   |         0 |          0    |               2 | 0                              |
| Category Id                   | int64   |         0 |          0    |              51 | 73                             |
| Category Name                 | str     |         0 |          0    |              50 | Sporting Goods                 |
| Customer City                 | str     |         0 |          0    |             563 | Caguas                         |
| Customer Country              | str     |         0 |          0    |               2 | Puerto Rico                    |
| Customer Email                | str     |         0 |          0    |               1 | XXXXXXXXX                      |
| Customer Fname                | str     |         0 |          0    |             782 | Cally                          |
| Customer Id                   | int64   |         0 |          0    |           20652 | 20755                          |
| Customer Lname                | str     |         8 |          0    |            1109 | Holloway                       |
| Customer Password             | str     |         0 |          0    |               1 | XXXXXXXXX                      |
| Customer Segment              | str     |         0 |          0    |               3 | Consumer                       |
| Customer State                | str     |         0 |          0    |              46 | PR                             |
| Customer Street               | str     |         0 |          0    |            7458 | 5365 Noble Nectar Island       |
| Customer Zipcode              | float64 |         3 |          0    |             995 | 725.0                          |
| Department Id                 | int64   |         0 |          0    |              11 | 2                              |
| Department Name               | str     |         0 |          0    |              11 | Fitness                        |
| Latitude                      | float64 |         0 |          0    |           11250 | 18.2514534                     |
| Longitude                     | float64 |         0 |          0    |            4487 | -66.03705597                   |
| Market                        | str     |         0 |          0    |               5 | Pacific Asia                   |
| Order City                    | str     |         0 |          0    |            3597 | Bekasi                         |
| Order Country                 | str     |         0 |          0    |             164 | Indonesia                      |
| Order Customer Id             | int64   |         0 |          0    |           20652 | 20755                          |
| order date (DateOrders)       | str     |         0 |          0    |           65752 | 1/31/2018 22:56                |
| Order Id                      | int64   |         0 |          0    |           65752 | 77202                          |
| Order Item Cardprod Id        | int64   |         0 |          0    |             118 | 1360                           |
| Order Item Discount           | float64 |         0 |          0    |            1017 | 13.10999966                    |
| Order Item Discount Rate      | float64 |         0 |          0    |              18 | 0.039999999                    |
| Order Item Id                 | int64   |         0 |          0    |          180519 | 180517                         |
| Order Item Product Price      | float64 |         0 |          0    |              75 | 327.75                         |
| Order Item Profit Ratio       | float64 |         0 |          0    |             162 | 0.289999992                    |
| Order Item Quantity           | int64   |         0 |          0    |               5 | 1                              |
| Sales                         | float64 |         0 |          0    |             193 | 327.75                         |
| Order Item Total              | float64 |         0 |          0    |            2927 | 314.6400146                    |
| Order Profit Per Order        | float64 |         0 |          0    |           21998 | 91.25                          |
| Order Region                  | str     |         0 |          0    |              23 | Southeast Asia                 |
| Order State                   | str     |         0 |          0    |            1089 | Java Occidental                |
| Order Status                  | str     |         0 |          0    |               9 | COMPLETE                       |
| Order Zipcode                 | float64 |    155679 |         86.24 |             609 | 99301.0                        |
| Product Card Id               | int64   |         0 |          0    |             118 | 1360                           |
| Product Category Id           | int64   |         0 |          0    |              51 | 73                             |
| Product Description           | float64 |    180519 |        100    |               0 | N/A                            |
| Product Image                 | str     |         0 |          0    |             118 | http://images.acmesports.sport |
| Product Name                  | str     |         0 |          0    |             118 | Smart watch                    |
| Product Price                 | float64 |         0 |          0    |              75 | 327.75                         |
| Product Status                | int64   |         0 |          0    |               1 | 0                              |
| shipping date (DateOrders)    | str     |         0 |          0    |           63701 | 2/3/2018 22:56                 |
| Shipping Mode                 | str     |         0 |          0    |               4 | Standard Class                 |
