# Superset BI setup for mart and ML use cases

This project uses the Olist Brazilian E-commerce public dataset, a dataset centered on Brazil's e-commerce market and collected by Olist from its marketplace operations.
It captures around 100,000 orders between 2016 and 2018 and covers the full business flow from order status, pricing, payment, freight, product attributes, customer location, and customer reviews to geolocation references linked from Brazilian zip codes to latitude and longitude.

That context is important because the BI layer here is not meant to be a generic dashboarding exercise.
It is designed to transform Olist's collected Brazil e-commerce data into business-facing analysis around commerce performance, delivery quality, product demand, and regional opportunity.

From a business perspective, the BI layer in this project is designed to answer three operational questions:
- which products are likely to become bestsellers soon so inventory and marketing can react earlier
- which orders are at risk of not becoming successful deliveries so operations can intervene sooner
- which cities or regions are likely to see higher demand so campaign planning and logistics readiness can be allocated more effectively

## 1. Start Superset

Run:

```bash
docker compose up -d postgres superset
```

Open:

```text
http://localhost:8088
```

Default login:

```text
username: admin
password: admin
```

## 2. Connect Superset to the ecommerce warehouse

In Superset:

1. Go to `Settings` -> `Database Connections`.
2. Click `+ Database`.
3. Choose PostgreSQL.
4. Use this SQLAlchemy URI:

```text
postgresql+psycopg2://airflow:airflow@postgres:5432/ecommerce
```

5. Test connection and save as:

```text
Ecommerce Mart
```

Inside Docker, the host is `postgres`. From your local machine, the same database is exposed as `localhost:5433`, but Superset must use the Docker service name.

## 3. Main schemas and tables

Use schema:

```text
marts
```

Core BI tables:

| Table | Use |
| --- | --- |
| `fact_orders` | Revenue, order volume, payment behavior, order status |
| `fact_order_items` | Product, seller, item value, freight |
| `fact_category_daily` | Category trend |
| `fact_product_daily` | Product trend |
| `fact_geo_daily` | City/state demand |
| `dim_customers` | Customer location/profile |
| `dim_products` | Product category and physical attributes |
| `dim_sellers` | Seller location/performance |

ML-ready tables:

| Table | Business question |
| --- | --- |
| `fact_ml_product_demand` | San pham nao sap ban chay? |
| `fact_ml_order_success` | Don hang nao co kha nang thanh cong? |
| `fact_ml_geo_demand` | Khu vuc nao co nhu cau mua cao? |

Superset-ready BI views:

| View | Dashboard role |
| --- | --- |
| `bi_superset_business_overview` | KPI tong quan dau dashboard |
| `bi_superset_product_bestseller` | Visual cho san pham sap ban chay |
| `bi_superset_order_success` | Visual cho don hang co kha nang thanh cong |
| `bi_superset_geo_demand` | Visual cho khu vuc co nhu cau cao |

## 4. Recommended datasets

Create these datasets in Superset. Prefer the `bi_superset_*` views because they already convert flags and labels into chart-friendly columns:

| Dataset | Physical table |
| --- | --- |
| `BI - Business Overview` | `marts.bi_superset_business_overview` |
| `BI - Product Bestseller` | `marts.bi_superset_product_bestseller` |
| `BI - Order Success` | `marts.bi_superset_order_success` |
| `BI - Geo Demand` | `marts.bi_superset_geo_demand` |

## 5. Dashboard layout for the 3 predictive use cases

Dashboard name:

```text
Ecommerce Predictive Mart
```

### Section 1: Business overview

Dataset: `BI - Business Overview`

Suggested charts:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Total Revenue | Big Number | `sum(revenue)` |
| Total Orders | Big Number | `sum(orders)` |
| Average Order Value | Big Number | `avg(avg_order_value)` |
| Delivered Rate | Big Number Percent | `avg(delivered_rate)` |
| Revenue by Date | Time-series Line Chart | time column `metric_date`, metric `sum(revenue)` |
| Predictive Signal Trend | Time-series Line Chart | time column `metric_date`, metrics `sum(next_7d_product_units_signal)`, `sum(next_7d_geo_orders_signal)` |

### Section 2: Product bestseller prediction

Dataset: `BI - Product Bestseller`

Suggested charts:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Top Product Demand Signal | Bar Chart | dimension `product_category`, metric `sum(next_7d_units_signal)` |
| Bestseller Rate by Category | Bar Chart | dimension `product_category`, metric `avg(bestseller_flag)` |
| Demand Band Mix | Donut Chart | dimension `demand_band`, metric `count(ml_sample_key)` |
| Demand Trend | Time-series Line Chart | time column `full_date`, metrics `sum(historical_units)`, `sum(next_7d_units_signal)` |
| Product Signal Table | Table | `product_key`, `product_category`, `historical_units`, `next_7d_units_signal`, `bestseller_label`, `demand_band` |

Supporting visuals:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Freight vs Demand | Scatter Plot | x `avg_freight_per_unit`, y `next_7d_units_signal`, series `product_category` |
| Weight Band Demand | Bar Chart | dimension `weight_band`, metric `sum(next_7d_units_signal)` |

Business story:

```text
Bang nay tra loi: nen day ton kho/marketing cho san pham nao trong 7 ngay toi?
```

### Section 3: Order success prediction

Dataset: `BI - Order Success`

Suggested charts:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Successful Order Rate | Big Number Percent | `avg(success_flag)` |
| Failed/Unavailable Order Rate | Big Number Percent | `avg(not_successful_flag)` |
| Success by Payment Type | Bar Chart | dimension `dominant_payment_type`, metric `avg(success_flag)` |
| Success by State | Bar Chart | dimension `customer_state`, metric `avg(success_flag)` |
| Value Band Mix | Donut Chart | dimension `order_value_band`, metric `sum(payment_value)` |
| Order Signal Table | Table | `order_key`, `customer_state`, `payment_value`, `dominant_payment_type`, `order_success_label`, `approval_speed_band` |

Supporting visuals:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Approval Speed vs Success | Bar Chart | dimension `approval_speed_band`, metric `avg(success_flag)` |
| Installment Impact | Bar Chart | dimension `installment_label`, metric `avg(success_flag)` |
| Freight Ratio by Result | Box Plot | dimension `order_success_label`, metric `freight_to_gross_ratio` |

Business story:

```text
Bang nay tra loi: don nao co kha nang thanh cong va yeu to thanh toan/dia ly anh huong ra sao?
```

### Section 4: Geo demand prediction

Dataset: `BI - Geo Demand`

Suggested charts:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Top Demand Locations | Bar Chart | dimension `location_key`, metric `sum(next_7d_orders_signal)` |
| High Demand Area Rate | Bar Chart | dimension `customer_state`, metric `avg(high_demand_area_flag)` |
| Demand Band Mix | Donut Chart | dimension `geo_demand_band`, metric `count(ml_sample_key)` |
| Regional Revenue Trend | Time-series Line Chart | time column `full_date`, metric `sum(historical_revenue)` |
| Geo Signal Table | Table | `customer_state`, `customer_city`, `historical_orders`, `next_7d_orders_signal`, `geo_demand_label`, `geo_demand_band` |

Supporting visuals:

| Chart | Viz type | Metrics / columns |
| --- | --- | --- |
| Review vs Demand | Scatter Plot | x `avg_review_score`, y `next_7d_orders_signal`, series `customer_state` |
| Late Delivery vs Demand | Scatter Plot | x `late_delivery_ratio`, y `next_7d_orders_signal`, series `customer_state` |
| AOV by Location | Bar Chart | dimension `location_key`, metric `avg(avg_revenue_per_order)` |

Business story:

```text
Bang nay tra loi: khu vuc nao nen uu tien campaign/logistics trong 7 ngay toi?
```

## 6. Useful SQL Lab queries

### Top products likely to sell well

```sql
select
    product_key,
    product_category,
    sum(total_items) as historical_units,
    sum(next_7d_units) as next_7d_units_signal,
    avg(case when is_bestseller_next_7d then 1 else 0 end) as bestseller_rate
from marts.fact_ml_product_demand
group by 1, 2
order by next_7d_units_signal desc
limit 30;
```

### Order success by payment type

```sql
select
    dominant_payment_type,
    count(*) as orders,
    avg(case when is_successful_order then 1 else 0 end) as success_rate,
    sum(total_payment_value) as revenue
from marts.fact_ml_order_success
group by 1
order by revenue desc;
```

### High demand locations

```sql
select
    customer_state,
    customer_city,
    sum(total_orders) as historical_orders,
    sum(next_7d_orders) as next_7d_orders_signal,
    avg(case when is_high_demand_area_next_7d then 1 else 0 end) as high_demand_rate
from marts.fact_ml_geo_demand
group by 1, 2
order by next_7d_orders_signal desc
limit 30;
```

The equivalent Superset-ready views are:

```sql
select * from marts.bi_superset_business_overview limit 10;
select * from marts.bi_superset_product_bestseller limit 10;
select * from marts.bi_superset_order_success limit 10;
select * from marts.bi_superset_geo_demand limit 10;
```
