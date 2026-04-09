# Business Vault mapping for Olist dataset

## Muc tieu

Business Vault trong du an nay khong chi dung de lam dashboard co ban.
No can tro thanh lop trung gian on dinh de:

- build datamart theo mo hinh `dim_*` va `fact_*`
- sinh feature cho cac bai toan ML
- cap nguon tin cay cho lop GenAI xu ly truy van ngon ngu tu nhien

## Dinh huong tong the

Raw Vault giu tinh trung thuc cua source.
Business Vault bo sung business rule, current snapshot va cac entity co nghia nghiep vu.
Mart la lop phuc vu BI, ML va GenAI.

## Business Vault toi thieu nen co

| Business Vault model | Grain | Nguon raw_vault | Business rule / gia tri them | Mart / ML phuc vu |
| --- | --- | --- | --- | --- |
| `pit_order_snapshot` | 1 dong / order | `hub_order`, `lnk_order_customer`, `sat_order_status`, `sat_order_timestamps`, `sat_customer_identity`, `sat_customer_address` | Gom current state cua order va customer | `fact_orders`, `fact_customer_orders`, order-level ML |
| `bridge_order_line` | 1 dong / order item | `lnk_order_product_seller`, `sat_order_item_details`, `sat_product_details`, `sat_seller_address`, `pit_order_snapshot` | Enrich line item voi product, seller, SLA, gross amount | `fact_order_items`, delivery ML, product/seller BI |
| `bridge_order_payment` | 1 dong / order | `lnk_order_payment`, `sat_order_payment_details`, `hub_order` | Chuan hoa payment, tong tien, dominant payment type, installment flags | `fact_orders`, `fact_payments`, payment BI |
| `bridge_customer_order` | 1 dong / customer analysis entity | `pit_order_snapshot`, `bridge_order_payment`, `lnk_order_review`, `sat_review_details` | Customer 360 cho retention, CLV, segmentation | `dim_customers`, `fact_customer_snapshot`, churn/repeat ML |

## Business Vault nen bo sung de dung du nghiep vu

### 1. Customer identity layer

| BV model de xuat | Grain | Nguon | Gia tri |
| --- | --- | --- | --- |
| `bridge_customer_identity` | 1 dong / `customer_id` | `hub_customer`, `sat_customer_identity` | Anh xa `customer_id -> customer_unique_id` de chuan hoa grain |
| `same_as_customer` | 1 dong / `customer_unique_id` | tong hop tu `bridge_customer_identity` | Gom nhieu `customer_id` cua cung mot nguoi mua |
| `bridge_customer_profile` | 1 dong / `customer_unique_id` | `same_as_customer`, orders, reviews, payments | Current customer 360 cho segmentation va loyalty |

Ly do:
- Olist co nhieu `customer_id` cho cung mot `customer_unique_id`
- Neu khong co lop nay thi retention, repeat purchase va CLV deu sai

### 2. Order and lifecycle layer

| BV model de xuat | Grain | Nguon | Gia tri |
| --- | --- | --- | --- |
| `pit_order_snapshot` nang cap | 1 dong / order / `as_of_date` neu can | order sats + customer sats + `as_of_date` | Snapshot dung nghia de backtest ML |
| `bridge_order_lifecycle` | 1 dong / order | `pit_order_snapshot` | Tach logic lead time, approval time, delivery cycle, cancellation flags |
| `bridge_order_fulfillment` | 1 dong / order | order + item + seller thong tin | Base cho SLA monitoring va delivery risk |

Ly do:
- Predict late delivery
- Predict low review score
- Build funnel BI va operational BI

### 3. Product and seller base layer

| BV model de xuat | Grain | Nguon | Gia tri |
| --- | --- | --- | --- |
| `bridge_product_master` | 1 dong / product | `sat_product_details` + category translation | Product dimension base |
| `bridge_seller_master` | 1 dong / seller | `sat_seller_address` + order line history | Seller dimension base |
| `bridge_product_performance_base` | 1 dong / product | line, review, payment aggregates | Product BI va demand ML |
| `bridge_seller_performance_base` | 1 dong / seller | line, review, fulfillment aggregates | Seller BI, seller risk, SLA |

Ly do:
- Product and seller la 2 entity trung tam cua BI va ML
- Tinh truoc metric co tinh tai su dung cao o BV se de ra mart hon

### 4. Review and service quality layer

| BV model de xuat | Grain | Nguon | Gia tri |
| --- | --- | --- | --- |
| `bridge_review_order` | 1 dong / order-review | `lnk_order_review`, `sat_review_details`, `hub_order`, `hub_review` | Lam sach review, co score band, comment flag, answer lag |
| `bridge_service_quality` | 1 dong / order | order lifecycle + review + payment | Base cho predict review thap va quality dashboard |

Ly do:
- Review score la label rat tot cho service quality ML
- GenAI sau nay co the giai thich tai sao don co nguy co review xau

### 5. Time series and forecasting layer

| BV model de xuat | Grain | Nguon | Gia tri |
| --- | --- | --- | --- |
| `bridge_category_daily_base` | 1 dong / category / day | order item + product | Forecast category |
| `bridge_seller_daily_base` | 1 dong / seller / day | order item + seller | Forecast seller revenue, seller operations |
| `bridge_geo_daily_base` | 1 dong / state-city / day | order, customer, seller | Forecast regional demand va delivery |

Ly do:
- Forecast can grain theo chuoi thoi gian
- De aggregated base o BV giup fact forecasting gon va on dinh

## Bai toan ML du kien va BV can dung

| Bai toan ML | Predict gi | Grain | BV can dung |
| --- | --- | --- | --- |
| Late delivery prediction | giao tre hay khong | order item | `bridge_order_line`, `bridge_order_fulfillment`, `bridge_seller_performance_base` |
| Low review score prediction | `review_score <= 2` hay khong | order | `bridge_review_order`, `bridge_service_quality`, `bridge_order_payment` |
| Repeat purchase prediction | co mua lai trong 30/60/90 ngay | `customer_unique_id + as_of_date` | `same_as_customer`, `bridge_customer_profile`, PIT order snapshot |
| Churn prediction | customer se im lang trong ky tiep theo | `customer_unique_id + as_of_date` | `bridge_customer_profile`, `fact_customer_snapshot` base |
| CLV / value tier | gia tri customer ky toi | `customer_unique_id + as_of_date` | `bridge_customer_profile`, payment va order history |
| Demand forecasting | order/revenue/quantity tuong lai | `date + category/seller/state` | `bridge_category_daily_base`, `bridge_seller_daily_base`, `bridge_geo_daily_base` |
| Seller risk scoring | seller co nguy co SLA xau / review xau | seller | `bridge_seller_performance_base`, `bridge_service_quality` |

## Datamart huong toi

| Mart huong toi | Nguon BV de dung |
| --- | --- |
| `mart.dim_date` | `as_of_date` |
| `mart.dim_customers` | `same_as_customer`, `bridge_customer_profile` |
| `mart.dim_products` | `bridge_product_master` |
| `mart.dim_sellers` | `bridge_seller_master` |
| `mart.dim_geography` | customer + seller address base |
| `mart.dim_product_category` | product master + translation |
| `mart.dim_payment_type` | bridge payment |
| `mart.dim_order_status` | order lifecycle |
| `mart.fact_orders` | `pit_order_snapshot`, `bridge_order_lifecycle`, `bridge_order_payment` |
| `mart.fact_order_items` | `bridge_order_line` |
| `mart.fact_payments` | order payment line detail + payment dim mapping |
| `mart.fact_reviews` | `bridge_review_order` |
| `mart.fact_customer_orders` | order snapshot + customer profile |
| `mart.fact_customer_monthly` | customer profile + fact orders aggregates |
| `mart.fact_seller_daily` | `bridge_seller_daily_base` |
| `mart.fact_product_daily` | `bridge_product_performance_base` |
| `mart.fact_category_daily` | `bridge_category_daily_base` |
| `mart.fact_geo_daily` | `bridge_geo_daily_base` |
| `mart.fact_customer_snapshot` | customer profile + PIT logic |
| `mart.fact_order_snapshot_ml` | order PIT logic |
| `mart.fact_delivery_line_snapshot` | order line + fulfillment snapshot |
| `mart.fact_demand_series` | category/seller/geo daily bases |

## GenAI se tich hop o dau

GenAI khong nen doc truc tiep Raw Vault.
No nen dung metadata va mart co nghia nghiep vu.

### Vai tro cua GenAI

- hieu cau hoi ngon ngu tu nhien
- mapping cau hoi vao metric, dimension, filter, grain
- chon giua BI query va ML prediction
- giai thich ket qua bang ngon ngu tu nhien

### Lop du lieu GenAI nen su dung

| Lop | Dung cho GenAI de lam gi |
| --- | --- |
| `dim_*` | hieu entity nghiep vu nhu customer, seller, product, date |
| `fact_*` | tra metric, trend, ranking, top-N |
| `fact_*_snapshot` | goi model ML tai dung cutoff phan tich |
| semantic metadata | map alias ngon ngu tu nhien sang ten truong warehouse |

### Vi du use case GenAI

- "Top seller nao co nguy co giao tre cao nhat tuan nay?"
- "Khach hang nao co nguy co churn o Sao Paulo?"
- "Du bao doanh thu category health_beauty thang toi"
- "Tai sao order nay co nguy co review thap?"

De tra loi duoc cac cau hoi nay, can co:
- mart on dinh
- model ML da train
- metadata metric/dimension ro rang

## Bo sung can co neu muon GenAI tot hon

### Structured metadata

Can co tai lieu hoac bang metadata mo ta:
- ten metric
- cong thuc metric
- grain
- dim/fact lien quan
- synonym tieng Viet va tieng Anh

### Prediction serving tables

Nen co cac bang:
- `fact_order_predictions`
- `fact_customer_predictions`
- `fact_seller_predictions`

Trong do luu:
- prediction timestamp
- model version
- score
- risk band
- top reason codes

### Text-ready explanation fields

Nen bo sung cho lop prediction:
- `top_reason_1`
- `top_reason_2`
- `top_reason_3`
- `recommended_action`

GenAI co the dung cac truong nay de tao cau tra loi tu nhien de doc hon.

## Thu tu uu tien phat trien

### Phase 1

- sua grain customer sang `customer_unique_id`
- nang cap `pit_order_snapshot`
- them `bridge_customer_identity`
- them `bridge_review_order`
- them `bridge_product_master`
- them `bridge_seller_master`

### Phase 2

- them `bridge_customer_profile`
- them `bridge_order_lifecycle`
- them `bridge_order_fulfillment`
- them `bridge_seller_performance_base`
- them `bridge_product_performance_base`

### Phase 3

- build dim/fact core
- build fact aggregate theo ngay/thang
- build fact snapshot cho ML

### Phase 4

- train ML models
- luu prediction vao fact predictions
- them metadata semantic layer cho GenAI
- build API hoac chatbot layer de nhan ngon ngu tu nhien

## Khong can uu tien ngay luc nay

| Model | Ly do chua can |
| --- | --- |
| PIT cho product/seller theo lich su day du | Dataset Olist it bien dong theo thoi gian o hai entity nay |
| Multi-currency BV | Olist chu yeu BRL, co the bo sung sau |
| Geolocation distance chinh xac | Nen lam sau khi geolocation mapping on dinh |

## Ket luan

Neu muc tieu cuoi cung la vua BI, vua ML, vua tich hop GenAI thi Business Vault hien tai la chua du.

Can phat trien them cac nhom BV sau:

- customer identity va customer profile
- order lifecycle va fulfillment
- product va seller master/performance
- review va service quality
- daily base cho forecasting

Tu do moi build mart `dim_*`, `fact_*`, cac bang prediction va semantic layer cho GenAI mot cach ben vung.
