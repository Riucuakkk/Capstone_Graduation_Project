# ML and GenAI strategy

## Muc tieu

Tai lieu nay tra loi 4 cau hoi:

1. Se predict cai gi truoc
2. Dung du lieu nao de predict
3. Can build them gi trong BV va mart
4. Sau nay GenAI se tich hop vao dau

## Bai toan ML uu tien

### 1. Late delivery prediction

Predict:
- `is_delivered_late`
- `shipped_after_limit`

Grain:
- uu tien `order_item`

Vi sao nen lam som:
- business value cao
- label kha sach
- de dua vao dashboard va alerting

Dung du lieu:
- `bridge_order_line`
- `bridge_order_fulfillment`
- `bridge_seller_performance_base`
- `dim_sellers`
- `dim_products`
- `dim_geography`

Feature chinh:
- product size, weight
- freight ratio
- seller region
- customer region
- shipping limit
- seller historical late ratio
- order purchase day-of-week/month

### 2. Low review score prediction

Predict:
- `review_score <= 2`

Grain:
- `order`

Dung du lieu:
- `bridge_review_order`
- `bridge_service_quality`
- `bridge_order_payment`
- `fact_orders`
- `fact_order_items`

Feature chinh:
- delivery cycle
- late delivery
- installment usage
- total payment
- seller quality history
- product review history

### 3. Repeat purchase prediction

Predict:
- customer co quay lai mua trong 30/60/90 ngay khong

Grain:
- `customer_unique_id + as_of_date`

Dung du lieu:
- `same_as_customer`
- `bridge_customer_profile`
- `fact_customer_snapshot`

Feature chinh:
- recency
- frequency
- monetary
- payment preferences
- review behavior
- category affinity
- delivery experience history

### 4. Churn prediction

Predict:
- customer se khong mua lai trong ky tiep theo

Grain:
- `customer_unique_id + as_of_date`

Dung du lieu:
- `bridge_customer_profile`
- `fact_customer_snapshot`

Feature chinh:
- recency trend
- order count trend
- revenue trend
- review trend
- late delivery exposure

### 5. CLV / value tier

Predict:
- value tier hoac doanh thu customer ky toi

Grain:
- `customer_unique_id + as_of_date`

Dung du lieu:
- `bridge_customer_profile`
- `fact_customer_monthly`
- `fact_customer_snapshot`

### 6. Demand forecasting

Predict:
- quantity
- revenue
- order count

Grain:
- `date + category`
- mo rong sang `seller` va `state`

Dung du lieu:
- `bridge_category_daily_base`
- `bridge_seller_daily_base`
- `bridge_geo_daily_base`
- `fact_demand_series`

## BV can bo sung de phuc vu ML

| Nhom | Model de xuat | Muc dich |
| --- | --- | --- |
| Customer identity | `bridge_customer_identity`, `same_as_customer` | dung grain customer |
| Customer analytics | `bridge_customer_profile` | base cho churn, repeat, CLV |
| Order lifecycle | `bridge_order_lifecycle` | base cho order risk va BI |
| Fulfillment | `bridge_order_fulfillment` | base cho late delivery |
| Review | `bridge_review_order`, `bridge_service_quality` | base cho review prediction |
| Product | `bridge_product_master`, `bridge_product_performance_base` | product BI va forecasting |
| Seller | `bridge_seller_master`, `bridge_seller_performance_base` | seller BI va seller risk |
| Time series | `bridge_category_daily_base`, `bridge_seller_daily_base`, `bridge_geo_daily_base` | forecasting |

## Mart can co de phuc vu ML va BI

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

### ML-ready marts

- `fact_customer_snapshot`
- `fact_order_snapshot_ml`
- `fact_delivery_line_snapshot`
- `fact_demand_series`
- `fact_order_predictions`
- `fact_customer_predictions`
- `fact_seller_predictions`

## Prediction serving layer

Sau khi train model, prediction khong nen chi nam trong notebook.
Nen luu xuong warehouse de BI va GenAI cung doc duoc.

### Bang prediction de xuat

| Model | Grain | Chua gi |
| --- | --- | --- |
| `fact_order_predictions` | 1 dong / order / prediction run | score, label du bao, model version, reason codes |
| `fact_customer_predictions` | 1 dong / customer / prediction run | churn score, repeat score, CLV tier, reason codes |
| `fact_seller_predictions` | 1 dong / seller / prediction run | seller risk, SLA risk, quality risk |

### Cac cot nen co

- `prediction_timestamp`
- `model_name`
- `model_version`
- `score`
- `predicted_class`
- `risk_band`
- `top_reason_1`
- `top_reason_2`
- `top_reason_3`
- `recommended_action`

## GenAI integration architecture

## Muc tieu cua GenAI

Cho phep nguoi dung nhap cau hoi tu nhien nhu:

- "Khach nao co nguy co churn cao nhat thang nay?"
- "Seller nao co SLA xau o Sao Paulo?"
- "Du bao doanh thu category toys trong 30 ngay toi"
- "Tai sao don hang nay bi danh gia nguy co review thap?"

## GenAI se dung du lieu gi

### Lop 1: Semantic metadata

Can co mot semantic layer mo ta:
- metric name
- business meaning
- grain
- allowed filters
- mapping synonym Viet/Anh

Vi du:
- "doanh thu", "revenue", "GMV"
- "khach hang", "customer", "nguoi mua"
- "giao tre", "late delivery", "tre han"

### Lop 2: BI data layer

GenAI doc:
- `dim_*`
- `fact_*`

De tra loi:
- tong hop KPI
- trend
- ranking
- slicing and dicing

### Lop 3: ML prediction layer

GenAI doc:
- `fact_*_predictions`
- `fact_*_snapshot`

De tra loi:
- risk
- du bao
- explanation
- recommended action

## Pipeline xu ly cau hoi ngon ngu tu nhien

1. NLU / intent detection
   Xac dinh user dang hoi:
   - BI question
   - ML prediction question
   - explanation question

2. Semantic mapping
   Anh xa tu khoa sang:
   - fact
   - dim
   - metric
   - filter
   - time grain

3. Query / retrieval routing
   - Neu la BI thi query `fact_*` + `dim_*`
   - Neu la ML thi query `fact_*_predictions`
   - Neu la explain thi query them reason codes

4. Response generation
   Tra loi bang ngon ngu tu nhien, co the kem bang top-N va insight

## Dieu kien de GenAI hoat dong tot

- grain mart phai ro
- metric phai duoc chuan hoa
- prediction phai duoc materialize vao warehouse
- reason codes phai co cau truc
- synonym business phai duoc map san

## Roadmap thuc hien

### Phase 1: Data foundation

- sua BV customer grain
- nang cap PIT
- them cac bridge BV can thiet

### Phase 2: Mart foundation

- build dim/fact core
- build fact aggregate
- build fact snapshot cho ML

### Phase 3: ML foundation

- train late delivery
- train low review score
- train repeat purchase / churn
- luu prediction vao `fact_*_predictions`

### Phase 4: GenAI layer

- tao semantic metadata
- tao service mapping intent -> query/prediction
- tao response generation layer

## Ket luan

Huong toi uu cho du an nay la:

- BI layer dua tren star schema
- ML layer dua tren snapshot facts va prediction facts
- GenAI layer dung semantic metadata + mart + prediction tables

Neu lam theo huong nay, he thong se co du kha nang de:
- dashboard duoc
- predict duoc
- va tra loi cau hoi ngon ngu tu nhien duoc
