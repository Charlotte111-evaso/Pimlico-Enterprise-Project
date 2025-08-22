-- Example SQL queries (SQLite-friendly)

SELECT Region, ROUND(SUM(Sales),2) AS Total_Sales
FROM Orders
GROUP BY Region
ORDER BY Total_Sales DESC;

SELECT "Product Name", ROUND(SUM(Profit),2) AS Total_Profit
FROM Orders
GROUP BY "Product Name"
ORDER BY Total_Profit DESC
LIMIT 10;

SELECT strftime('%Y-%m', "Order Date") AS Month, ROUND(Sales,2) AS Revenue
FROM Orders
GROUP BY Month
ORDER BY Month;
