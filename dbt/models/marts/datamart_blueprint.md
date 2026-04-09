# Datamart blueprint for BI and ML

## Muc tieu

Datamart cuoi cung van theo mo hinh star schema, nghia la chi dua ra `dim_*` va `fact_*`.
Business Vault la lop trung gian de chuan hoa business rule, con mart la lop phuc vu dashboard, ad-hoc analysis va feature extraction cho ML.

Voi bo du lieu Olist va dinh huong sap toi, 4 dim va 4 fact la chua du. Nen phat trien datamart day du hon theo nhom nghiep vu.

## Nguyen tac thiet ke

1. Toan bo dau ra cho nguoi dung cuoi deu la `dim_*` va `fact_*`.
2. Cac fact phai ro grain va ro event date.
3. Cac dim phai ro business entity, uu tien khoa phan tich on dinh.
4. Feature cho ML nen lay tu dim/fact va neu can snapshot thi van dong goi duoi dang fact snapshot.
5. Customer analytics uu tien `customer_unique_id` hon `customer_id`.

## Bo dim de xuat

### Nhom core dimensions

| Model | Grain | Nguon chinh | Muc dich |
| --- | --- | --- | --- |
| `dim_date` | 1 dong / ngay | `as_of_date` | Calendar chung cho BI, cohort, forecast, snapshot ML |
| `dim_customers` | 1 dong / `customer_unique_id` | `bridge_customer_order`, `pit_order_snapshot`, `sat_customer_identity`, `sat_customer_address` | Customer 360, retention, CLV, segmentation |
| `dim_products` | 1 dong / `product_id` | `sat_product_details`, `bridge_order_line` | Thuoc tinh san pham, category, size, weight |
| `dim_sellers` | 1 dong / `seller_id` | `sat_seller_address`, `bridge_order_line` | Seller 360, khu vuc, SLA, performance |

### Nhom dimensions mo rong

| Model | Grain | Nguon chinh | Muc dich |
| --- | --- | --- | --- |
| `dim_geography` | 1 dong / city-state-zip prefix | `sat_customer_address`, `sat_seller_address`, `geolocation` | Phan tich dia ly, shipping lane, regional BI |
| `dim_product_category` | 1 dong / product category | `products`, `product_category_name_translation` | Dashboard theo nganh hang va forecast theo category |
| `dim_payment_type` | 1 dong / payment type | `bridge_order_payment`, `order_payments` | Chuan hoa hanh vi thanh toan |
| `dim_order_status` | 1 dong / status | `sat_order_status` | Dashboard status funnel, SLA pipeline |
| `dim_review_band` | 1 dong / nhom diem review | quy uoc nghiep vu | Nhom hai long/khong hai long cho BI va ML |
| `dim_delivery_sla_band` | 1 dong / nhom SLA | suy ra tu `bridge_order_line`, `pit_order_snapshot` | Phan loai giao som, dung han, tre |

## Bo fact de xuat

### Nhom core transaction facts

| Model | Grain | Nguon chinh | Muc dich |
| --- | --- | --- | --- |
| `fact_orders` | 1 dong / order | `pit_order_snapshot` + `bridge_order_payment` | KPI order, revenue, order lifecycle, AOV |
| `fact_order_items` | 1 dong / order item | `bridge_order_line` | Product BI, seller BI, SLA, line margin proxy |
| `fact_payments` | 1 dong / payment transaction | `lnk_order_payment` + `sat_order_payment_details` + `hub_order` | Payment mix, installment analysis, fraud/risk proxy |
| `fact_reviews` | 1 dong / review-order | `lnk_order_review` + `sat_review_details` + `hub_review` + `hub_order` | Review score, complaint proxy, service quality |

### Nhom facts tong hop cho BI

| Model | Grain | Nguon chinh | Muc dich |
| --- | --- | --- | --- |
| `fact_customer_orders` | 1 dong / customer-order | `pit_order_snapshot` + `bridge_order_payment` + `review_summary` | Retention, order sequence, customer journey |
| `fact_customer_monthly` | 1 dong / customer / month | tong hop tu `fact_orders` | Cohort, active customer, CLV theo thang |
| `fact_seller_daily` | 1 dong / seller / day | tong hop tu `fact_order_items` | Seller performance dashboard, SLA, revenue trend |
| `fact_product_daily` | 1 dong / product / day | tong hop tu `fact_order_items` | Demand trend, category movement, stock proxy |
| `fact_category_daily` | 1 dong / category / day | tong hop tu `fact_order_items` + `dim_product_category` | Forecast doanh thu/san luong theo category |
| `fact_geo_daily` | 1 dong / state-city / day | tong hop tu `fact_orders`, `fact_order_items` | Regional BI, logistics performance |

### Nhom facts snapshot cho ML nhung van giu star schema

| Model | Grain | Nguon chinh | Muc dich |
| --- | --- | --- | --- |
| `fact_customer_snapshot` | 1 dong / `customer_unique_id` / `as_of_date` | snapshot tu orders, payments, reviews | Churn, repeat purchase, CLV, segmentation |
| `fact_order_snapshot_ml` | 1 dong / order / cutoff date | snapshot tu order lifecycle | Predict cancel, late delivery, review risk |
| `fact_delivery_line_snapshot` | 1 dong / order item / cutoff date | snapshot tu `fact_order_items` | Predict line-level late shipment |
| `fact_demand_series` | 1 dong / date / entity forecast | tong hop tu `fact_order_items` | Forecast doanh thu, quantity theo category/seller/state |

## Goi y mapping tu Business Vault sang mart

| BV model | Mart dung lai duoc |
| --- | --- |
| `pit_order_snapshot` | `fact_orders`, `fact_customer_orders`, `fact_order_snapshot_ml` |
| `bridge_order_line` | `fact_order_items`, `fact_seller_daily`, `fact_product_daily`, `fact_delivery_line_snapshot` |
| `bridge_order_payment` | `fact_orders`, `fact_payments`, `dim_payment_type`, `fact_customer_snapshot` |
| `bridge_customer_order` | `dim_customers`, `fact_customer_monthly`, `fact_customer_snapshot` |
| `as_of_date` | `dim_date` va tat ca cac bang snapshot |

## Nhu cau sua Business Vault truoc khi build mart day du

### 1. Customer grain

Can doi trung tam phan tich customer tu `customer_id` sang `customer_unique_id`.

Neu giu `customer_id` lam grain cho `dim_customers`:
- sai retention
- sai repeat purchase
- sai CLV
- sai segmentation cho cung mot nguoi mua

### 2. PIT dung nghia

`pit_order_snapshot` hien tai la latest snapshot, chua phai point-in-time theo `as_of_date`.

Can nang cap de co the sinh:
- `fact_order_snapshot_ml`
- `fact_customer_snapshot`
- backtest feature theo cutoff

### 3. Tach BV va mart cho ro

Nen giu BV o muc:
- order business snapshot
- order line business enrichment
- payment business summary
- customer business summary
- review business summary

Khong nen nhom qua nhieu aggregate phuc vu dashboard cu the vao BV neu aggregate do chi dung cho 1 mart.

### 4. Bo sung business entities cho BV

De datamart day du hon, nen them:

| BV de xuat bo sung | Grain | Gia tri |
| --- | --- | --- |
| `bridge_review_order` | 1 dong / order-review | Tach review logic sach hon cho `fact_reviews` |
| `bridge_customer_identity` hoac `same_as_customer` | 1 dong / `customer_unique_id` | Gom cac `customer_id` thuoc cung mot customer |
| `bridge_seller_performance_base` | 1 dong / seller | Lam base cho seller mart va seller ML |
| `bridge_product_performance_base` | 1 dong / product | Lam base cho product/category mart |

## Uu tien build datamart theo phase

### Phase 1: Core BI

- `dim_date`
- `dim_customers`
- `dim_products`
- `dim_sellers`
- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

### Phase 2: Business performance marts

- `dim_geography`
- `dim_product_category`
- `dim_payment_type`
- `dim_order_status`
- `fact_customer_orders`
- `fact_customer_monthly`
- `fact_seller_daily`
- `fact_product_daily`
- `fact_category_daily`
- `fact_geo_daily`

### Phase 3: ML-ready marts

- `fact_customer_snapshot`
- `fact_order_snapshot_ml`
- `fact_delivery_line_snapshot`
- `fact_demand_series`

## Danh sach nghiep vu duoc phuc vu

### BI

- Doanh thu theo ngay, thang, category, seller, geography
- Order funnel theo status
- AOV, payment mix, installment behavior
- Delivery SLA, late delivery ratio
- Product and seller performance
- Review score va complaint proxy
- Customer retention va repeat purchase

### ML

- Churn prediction
- Repeat purchase prediction
- CLV estimation
- Delivery delay prediction
- Low review score prediction
- Demand forecasting theo category, seller, state
- Seller risk scoring
- Customer segmentation

## Ket luan

Datamart day du cho du an nay nen theo huong:

- Khoang 8-10 dimension
- Khoang 10-14 fact tuy muc do mo rong

Khong nen dung lai o 4 dim va 4 fact neu muc tieu la vua BI vua ML.
Tuy nhien cung khong nen build tat ca mot luc. Nen build theo phase va sua lai Business Vault de customer grain va snapshot grain dung ngay tu dau.
