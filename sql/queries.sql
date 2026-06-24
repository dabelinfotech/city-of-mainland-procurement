-- ============================================================
-- City of Mainland — Procurement Analysis
-- SQL statements for the four required dashboard questions.
-- Dialect: T-SQL (SQL Server). Adjust TOP/LIMIT for other engines.
-- Tables: Category, Product, ProductCategory, PurchaseTrans
-- ============================================================


-- ------------------------------------------------------------
-- Q1. Join all tables: ProductName, ProductNumber + PurchaseTrans
-- ------------------------------------------------------------
SELECT
    p.ProductName,
    p.ProductNumber,
    pt.*
FROM PurchaseTrans          AS pt
INNER JOIN Product          AS p  ON pt.ProductID  = p.ProductID
INNER JOIN ProductCategory  AS pc ON p.ProductID   = pc.ProductID
INNER JOIN Category         AS c  ON pc.CategoryID = c.CategoryID;


-- ------------------------------------------------------------
-- Q2. Top 10 products ordered per country on a specific date,
--     with category detail and net amount (drill-down).
-- Net = (UnitPrice * Qty) - (UnitPriceDiscount * UnitPrice * Qty)
-- ------------------------------------------------------------
SELECT TOP 10
    pt.Country,
    p.ProductName,
    p.ProductNumber,
    c.CategoryName,
    SUM(pt.OrderQty)                                            AS TotalQty,
    SUM(pt.UnitPrice * pt.OrderQty)                             AS PurchasedAmount,
    SUM(pt.UnitPriceDiscount * pt.UnitPrice * pt.OrderQty)      AS DiscountAmount,
    SUM(pt.UnitPrice * pt.OrderQty)
        - SUM(pt.UnitPriceDiscount * pt.UnitPrice * pt.OrderQty) AS NetPurchaseAmount
FROM PurchaseTrans pt
JOIN Product          p  ON pt.ProductID  = p.ProductID
JOIN ProductCategory  pc ON p.ProductID   = pc.ProductID
JOIN Category         c  ON pc.CategoryID = c.CategoryID
WHERE pt.Country   = @Country     -- e.g. 'United States'
  AND pt.OrderDate = @OrderDate    -- e.g. '2013-07-31'
GROUP BY pt.Country, p.ProductName, p.ProductNumber, c.CategoryName
ORDER BY SUM(pt.OrderQty) DESC;


-- ------------------------------------------------------------
-- Q3. Suppliers offering a discount, filtered by Product Category
-- ------------------------------------------------------------
SELECT
    pt.Supplier,
    c.CategoryName,
    COUNT(*)                                                AS DiscountedLines,
    SUM(pt.UnitPriceDiscount * pt.UnitPrice * pt.OrderQty)  AS TotalDiscountAmount
FROM PurchaseTrans pt
JOIN Product          p  ON pt.ProductID  = p.ProductID
JOIN ProductCategory  pc ON p.ProductID   = pc.ProductID
JOIN Category         c  ON pc.CategoryID = c.CategoryID
WHERE pt.UnitPriceDiscount > 0
  AND c.CategoryName = @CategoryName     -- slicer-driven
GROUP BY pt.Supplier, c.CategoryName
ORDER BY TotalDiscountAmount DESC;


-- ------------------------------------------------------------
-- Q4. Geographic total by class, drill Country > State > City,
--     with product info and purchased amount.
-- ------------------------------------------------------------
SELECT
    pt.Class,
    pt.Country,
    pt.StateProvince,
    pt.City,
    p.ProductName,
    SUM(pt.OrderQty)                AS TotalQty,
    SUM(pt.UnitPrice * pt.OrderQty) AS PurchasedAmount,
    SUM(pt.UnitPrice * pt.OrderQty)
        - SUM(pt.UnitPriceDiscount * pt.UnitPrice * pt.OrderQty) AS NetPurchaseAmount
FROM PurchaseTrans pt
JOIN Product p ON pt.ProductID = p.ProductID
GROUP BY pt.Class, pt.Country, pt.StateProvince, pt.City, p.ProductName
ORDER BY pt.Class, pt.Country, pt.StateProvince, pt.City;
