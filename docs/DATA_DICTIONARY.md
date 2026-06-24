# Data Dictionary

Star-schema model used by the Power BI report. Fact table `PurchaseTrans`
joins to `DimProduct`, which joins to `DimCategory`.

## PurchaseTrans (fact) — 26,357 rows

| Column | Type | Description |
|---|---|---|
| TransID | int | Unique transaction line ID (primary key) |
| OrderID | int | Purchase order ID (groups lines) |
| AccountNumber | text | Account reference |
| Supplier | text | Supplier / sales contact name |
| Address, City, PostalCode, StateProvince, Country | text | Ship-to geography. Missing `PostalCode` cleaned to `Unknown` |
| Employee | text | Owning employee |
| DueDate, ShipDate, OrderDate | date | Order lifecycle dates |
| CarrierTrackingNumber | text | Shipment tracking |
| ProductID | int | FK → DimProduct |
| OrderQty | int | Units ordered |
| Class | text | Product class: High / Medium / Low |
| Color | text | Product color. Missing values cleaned to `Not Specified` |
| ListPrice | decimal | List price |
| SpecialOfferID | int | Promotion reference |
| UnitPrice | decimal | Actual unit price paid |
| UnitPriceDiscount | decimal | Discount factor (0.00–0.40) |
| **PurchasedAmount** | decimal | Derived: `UnitPrice * OrderQty` |
| **DiscountAmount** | decimal | Derived: `UnitPriceDiscount * PurchasedAmount` |
| **NetPurchaseAmount** | decimal | Derived: `PurchasedAmount - DiscountAmount` |
| OrderYear | int | Derived from OrderDate |
| OrderMonth | text | Derived `YYYY-MM` from OrderDate |

## DimProduct — 104 rows

| Column | Type | Description |
|---|---|---|
| ProductID | int | Primary key |
| ProductName | text | Product display name |
| ProductNumber | text | SKU / product number |
| CategoryID | int | FK → DimCategory |
| CategoryName | text | Denormalised category name |

## DimCategory — 37 rows

| Column | Type | Description |
|---|---|---|
| CategoryID | int | Primary key |
| CategoryName | text | Category name (e.g. Road Bikes, Mountain Bikes) |

## Calculation rules (from project brief)

```
Purchased Amount    = UnitPrice * OrderQty
Discount Amount     = UnitPriceDiscount * Purchased Amount
Net Purchase Amount = Purchased Amount - Discount Amount
```

## KPI thresholds (CAD)

| Net Purchase Amount | Band |
|---|---|
| < 10,000 | Low |
| 10,000 – 20,000 | Medium |
| > 20,000 | HIGH |
