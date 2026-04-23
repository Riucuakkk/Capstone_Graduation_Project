# ML and GenAI strategy

## Muc tieu

Tai lieu nay chot pham vi ML hien tai con 3 bai toan tieu bieu de giam khoi luong mart, nhung van du de demo BI + ML + GenAI:

1. San pham nao sap ban chay
2. Don hang nao co kha nang hoan tat thanh cong
3. Khu vuc nao co nhu cau mua hang cao

## Bai toan ML uu tien

| Task | Predict | Grain | ML mart |
| --- | --- | --- | --- |
| `product_bestseller` | San pham nam trong top demand 7 ngay toi | product-day | `fact_ml_product_demand` |
| `order_success` | Order co ket thuc bang delivered sale | order | `fact_ml_order_success` |
| `geo_high_demand` | City-state nam trong top demand 7 ngay toi | location-day | `fact_ml_geo_demand` |

## Feature source

| ML mart | Nguon chinh | Feature chinh |
| --- | --- | --- |
| `fact_ml_product_demand` | `fact_product_daily`, `dim_products` | category, kich thuoc/khoi luong, calendar, lag, rolling demand |
| `fact_ml_order_success` | `fact_orders`, `dim_customers` | basket, payment, installment, customer location |
| `fact_ml_geo_demand` | `fact_geo_daily` | location, calendar, orders/revenue, SLA/review, lag, rolling demand |

## Mart can co

### Core marts

- `dim_date`
- `dim_customers`
- `dim_products`
- `dim_sellers`
- `dim_geography`
- `dim_product_category`
- `dim_payment_type`
- `dim_order_status`
- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`
- `fact_customer_orders`
- `fact_customer_monthly`
- `fact_seller_daily`
- `fact_product_daily`
- `fact_category_daily`
- `fact_geo_daily`

### ML-ready marts

- `fact_ml_product_demand`
- `fact_ml_order_success`
- `fact_ml_geo_demand`

## GenAI integration architecture

GenAI nen doc semantic metadata va mart co nghia nghiep vu, khong doc truc tiep Raw Vault.

### Lop 1: Semantic metadata

Can co mo ta:

- metric name
- business meaning
- grain
- allowed filters
- mapping synonym Viet/Anh

Vi du:

- "san pham ban chay" -> `product_bestseller`, `fact_ml_product_demand`
- "don thanh cong" -> `order_success`, `fact_ml_order_success`
- "dia diem de mua" -> `geo_high_demand`, `fact_ml_geo_demand`

### Lop 2: BI data layer

GenAI doc `dim_*` va `fact_*` de tra loi KPI, trend, ranking, slicing.

### Lop 3: ML prediction layer

Trong giai doan hien tai, GenAI co the doc output tu CLI/API/Streamlit. Chi nen materialize prediction facts sau khi 3 model co metric chap nhan duoc.

## Pipeline xu ly cau hoi ngon ngu tu nhien

1. NLU / intent detection: BI question hay ML prediction question
2. Semantic mapping: map tu khoa sang fact/dim/task/metric
3. Query routing: BI query mart, ML goi task tu `src/ml`
4. Response generation: tra loi bang ngon ngu tu nhien, kem top-N/action neu can

## Roadmap

| Phase | Noi dung |
| --- | --- |
| Phase 1 | Build core BI marts |
| Phase 2 | Build daily aggregate facts cho product/category/seller/geo |
| Phase 3 | Build 3 `fact_ml_*` marts |
| Phase 4 | Train 3 model va demo tren Streamlit |
| Phase 5 | Neu can, them prediction write-back va explanation fields |

## Ket luan

Huong toi uu luc nay la lam sau 3 use case trong mot scope gon. Sau khi 3 task nay chay tot, moi nen mo rong sang churn, review risk, seller risk hoac prediction serving tables.
