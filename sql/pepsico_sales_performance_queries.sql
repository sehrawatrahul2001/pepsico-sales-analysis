-- ============================================================
-- PepsiCo Sales Performance & Business Insights Analysis | SQL Query Pack
-- Author: Rahul Sehrawat
-- Role Context: Assistant Manager (Operations) transitioning to Data Analytics
-- Assumption: PostgreSQL-compatible syntax
-- Source Table: pepsico_sales
-- Columns:
--   state, city, order_date, distributor_name, location,
--   beverage_category, beverage_name, price_inr, rating, rating_count
-- ============================================================

-- 1. Executive KPI Summary
SELECT
    COUNT(*)                  AS total_orders,
    ROUND(SUM(price_inr), 2)  AS total_revenue_inr,
    ROUND(AVG(price_inr), 2)  AS average_order_value_inr,
    ROUND(AVG(rating), 2)     AS average_rating
FROM pepsico_sales;


-- 2. Top 10 Products by Revenue
SELECT
    beverage_name,
    COUNT(*)                  AS total_orders,
    ROUND(SUM(price_inr), 2)  AS total_revenue_inr,
    ROUND(AVG(price_inr), 2)  AS avg_order_value_inr
FROM pepsico_sales
GROUP BY beverage_name
ORDER BY total_revenue_inr DESC
LIMIT 10;


-- 3. Monthly Sales Trend
SELECT
    DATE_TRUNC('month', order_date) AS sales_month,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(price_inr), 2)        AS total_revenue_inr,
    ROUND(AVG(price_inr), 2)        AS average_order_value_inr
FROM pepsico_sales
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY sales_month;


-- 4. Region-wise Sales Performance
SELECT
    state,
    city,
    COUNT(*)                  AS total_orders,
    ROUND(SUM(price_inr), 2)  AS total_revenue_inr,
    ROUND(AVG(rating), 2)     AS avg_rating
FROM pepsico_sales
GROUP BY state, city
ORDER BY total_revenue_inr DESC;


-- 5. Commercial Segmentation by Order Value
-- Note: Customer IDs are not available in the dataset,
-- so value bands are used as a business proxy for segmentation.
WITH value_segments AS (
    SELECT
        CASE
            WHEN price_inr <= 100 THEN 'Budget'
            WHEN price_inr <= 250 THEN 'Core'
            WHEN price_inr <= 500 THEN 'Premium'
            ELSE 'Enterprise'
        END AS customer_segment,
        price_inr,
        rating,
        rating_count
    FROM pepsico_sales
)
SELECT
    customer_segment,
    COUNT(*)                      AS total_orders,
    ROUND(SUM(price_inr), 2)      AS total_revenue_inr,
    ROUND(AVG(rating), 2)         AS avg_rating,
    ROUND(AVG(rating_count), 2)   AS avg_rating_count
FROM value_segments
GROUP BY customer_segment
ORDER BY total_revenue_inr DESC;


-- 6. Window Function Query:
-- Rank the top 3 products within each state by revenue
WITH product_state_revenue AS (
    SELECT
        state,
        beverage_name,
        ROUND(SUM(price_inr), 2) AS total_revenue_inr
    FROM pepsico_sales
    GROUP BY state, beverage_name
),
ranked_products AS (
    SELECT
        state,
        beverage_name,
        total_revenue_inr,
        DENSE_RANK() OVER (
            PARTITION BY state
            ORDER BY total_revenue_inr DESC
        ) AS revenue_rank
    FROM product_state_revenue
)
SELECT
    state,
    beverage_name,
    total_revenue_inr,
    revenue_rank
FROM ranked_products
WHERE revenue_rank <= 3
ORDER BY state, revenue_rank, total_revenue_inr DESC;
