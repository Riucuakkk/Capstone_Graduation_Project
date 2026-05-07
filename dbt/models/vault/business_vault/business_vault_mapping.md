# Business Vault mapping for Olist dataset

## Muc tieu

Business Vault la lop trung gian on dinh de:

- build datamart theo mo hinh `dim_*` va `fact_*`
- tao daily aggregate base cho BI
- cap feature cho 3 bai toan ML dang uu tien

Scope ML hien tai duoc thu gon de tranh phinh mart: product demand, order success, va geo demand.

## Business Vault toi thieu nen co

| Business Vault model | Grain | Business rule / gia tri them | Mart / ML phuc vu |
| --- | --- | --- | --- |
| `bridge_order_lifecycle` | 1 order | Lead time, approval state, delivered/canceled/unavailable flags | `fact_orders`, `fact_ml_order_success` |
| `bridge_order_fulfillment` | 1 order | Item summary, seller/product count, delivery metrics | `fact_orders`, BI delivery KPI |
| `bridge_order_line` | 1 order item | Product, seller, gross amount, freight, item-level status | `fact_order_items`, `fact_product_daily` |
| `bridge_order_payment` | 1 order | Payment total, dominant payment, installment flags | `fact_orders`, `fact_payments`, `fact_ml_order_success` |
| `bridge_customer_profile` | 1 customer_unique_id | Customer 360 current profile | `dim_customers`, order/customer BI |
| `bridge_product_master` | 1 product | Product category and physical attributes | `dim_products`, `fact_ml_product_demand` |
| `bridge_seller_master` | 1 seller | Seller location and performance summary | `dim_sellers`, seller BI |
| `bridge_service_quality` | 1 order | Review score/comment and service quality band | `fact_reviews`, geo/customer BI |

## 3 bai toan ML va BV can dung

| Bai toan ML | Predict gi | Grain | BV/mart source |
| --- | --- | --- | --- |
| `product_bestseller` | San pham co kha nang ban chay trong 7 ngay toi | product-day | `bridge_product_master`, `bridge_order_line`, `fact_product_daily` |
| `order_success` | Don co kha nang thanh cong/giao thanh cong | order | `bridge_order_lifecycle`, `bridge_order_payment`, `bridge_customer_profile`, `fact_orders` |
| `geo_high_demand` | Khu vuc co nhu cau mua cao trong 7 ngay toi | city-state-day | order/customer address trong BV, `fact_geo_daily` |

## Datamart hien tai

| Mart | Nguon BV de dung |
| --- | --- |
| `marts.dim_date` | `as_of_date` |
| `marts.dim_customers` | `bridge_customer_profile` |
| `marts.dim_products` | `bridge_product_master` |
| `marts.dim_sellers` | `bridge_seller_master` |
| `marts.dim_geography` | staging geolocation/customer/seller address |
| `marts.dim_product_category` | `bridge_product_master` |
| `marts.dim_payment_type` | `bridge_order_payment` |
| `marts.dim_order_status` | `bridge_order_lifecycle` |
| `marts.fact_orders` | `bridge_order_lifecycle`, `bridge_order_fulfillment`, `bridge_order_payment`, `bridge_service_quality` |
| `marts.fact_order_items` | `bridge_order_line`, `bridge_product_master` |
| `marts.fact_payments` | order payment link/detail |
| `marts.fact_reviews` | review/order service quality |
| `marts.fact_customer_orders` | `fact_orders` + customer profile |
| `marts.fact_customer_monthly` | `fact_customer_orders` |
| `marts.fact_seller_daily` | `fact_order_items` |
| `marts.fact_product_daily` | `fact_order_items` |
| `marts.fact_category_daily` | `fact_order_items` |
| `marts.fact_geo_daily` | `fact_orders` + customer geography |
| `marts.fact_ml_product_demand` | `fact_product_daily`, `dim_products` |
| `marts.fact_ml_order_success` | `fact_orders`, `dim_customers` |
| `marts.fact_ml_geo_demand` | `fact_geo_daily` |

## GenAI se tich hop o dau

GenAI khong nen doc truc tiep Raw Vault. No nen dung:

- `dim_*` de hieu entity: customer, product, seller, geography, date
- `fact_*` de tra KPI, trend, ranking, top-N
- `fact_ml_*` va output model tu `src/ml` de tra cau hoi du doan
- semantic metadata de map tu khoa tieng Viet/tieng Anh sang bang/cot/task

### Vi du use case GenAI phu hop voi scope moi

- "San pham nao sap ban chay trong 7 ngay toi?"
- "Don nao co kha nang giao thanh cong thap?"
- "Khu vuc nao nen day campaign?"
- "Vi sao model goi y uu tien san pham nay?"

## Thu tu uu tien phat trien

| Phase | Noi dung |
| --- | --- |
| Phase 1 | On dinh Business Vault cho order, product, customer, payment |
| Phase 2 | Build core dim/fact va daily aggregate facts |
| Phase 3 | Build 3 `fact_ml_*` marts |
| Phase 4 | Train 3 model va demo Streamlit |
| Phase 5 | Neu can, them prediction write-back va explanation fields |

## Ket luan

Business Vault hien tai nen phuc vu mart gon va thuc dung. Khi 3 bai toan ML chay tot, co metric tot va can demo sau hon, moi nen mo rong sang churn, review risk, seller risk hoac prediction serving tables.
