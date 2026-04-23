# Datamart blueprint for BI and 3 ML use cases

## Muc tieu

Tầng mart vẫn giữ star schema cho BI (`dim_*`, `fact_*`), nhưng phần ML được thu gọn còn 3 bài toán đại diện để dễ triển khai, dễ giải thích trong báo cáo và giảm số bảng snapshot/prediction phải bảo trì.

## Nguyen tac thiet ke

1. Core BI mart giữ vai trò nguồn sự thật: order, order item, payment, review, customer, product, seller, geography.
2. ML mart chỉ materialize 3 bảng feature/target rõ grain, không tạo nhiều bảng placeholder.
3. Target ML phải có ý nghĩa dự đoán tương lai hoặc kết quả cần ra quyết định, tránh chỉ tái tạo KPI hiện tại.
4. Mỗi bảng ML-ready phải trả lời được một câu hỏi nghiệp vụ cụ thể.

## Core marts duoc giu lai

### Dimensions

| Model | Grain | Muc dich |
| --- | --- | --- |
| `dim_date` | 1 dong / ngay | Calendar chung |
| `dim_customers` | 1 dong / customer_unique_id | Customer profile |
| `dim_products` | 1 dong / product_id | Product attributes/category |
| `dim_sellers` | 1 dong / seller_id | Seller profile |
| `dim_geography` | 1 dong / zip-city-state | Geography lookup |
| `dim_product_category` | 1 dong / category | Category chuẩn hóa |
| `dim_payment_type` | 1 dong / payment type | Payment mix |
| `dim_order_status` | 1 dong / status | Order status |

### Facts

| Model | Grain | Muc dich |
| --- | --- | --- |
| `fact_orders` | 1 dong / order | KPI order, payment summary, lifecycle |
| `fact_order_items` | 1 dong / order item | Product/seller/revenue line detail |
| `fact_payments` | 1 dong / payment transaction | Payment behavior |
| `fact_reviews` | 1 dong / review-order | Service quality |
| `fact_customer_orders` | 1 dong / customer-order | Customer journey |
| `fact_customer_monthly` | 1 dong / customer / month | Retention/cohort |
| `fact_seller_daily` | 1 dong / seller / ngay | Seller performance |
| `fact_product_daily` | 1 dong / product / ngay | Product demand base |
| `fact_category_daily` | 1 dong / category / ngay | Category dashboard |
| `fact_geo_daily` | 1 dong / city-state / ngay | Regional demand base |

## 3 ML-ready marts

| Model | Grain | Business question | Target |
| --- | --- | --- | --- |
| `fact_ml_product_demand` | 1 product / ngay co ban | San pham nao sap ban chay? | `is_bestseller_next_7d` |
| `fact_ml_order_success` | 1 order | Don hang nao co kha nang thanh cong/giao thanh cong? | `is_successful_order` |
| `fact_ml_geo_demand` | 1 city-state / ngay co ban | Dia diem nao de phat sinh mua hang? | `is_high_demand_area_next_7d` |

## Mapping nghiep vu

### 1. Product bestseller prediction

- Nguon: `fact_product_daily` + `dim_products`
- Dung cho: demand planning, ton kho, chon san pham day campaign
- Feature chinh: category, kich thuoc/khoi luong san pham, ngay/thang/thu, so luong/doanh thu hien tai, lag va rolling average
- Target: san pham co nam trong nhom top demand 7 ngay tiep theo hay khong

### 2. Order success prediction

- Nguon: `fact_orders` + `dim_customers`
- Dung cho: uu tien xu ly don, phat hien don can can thiep som
- Feature chinh: basket size, gia tri hang/freight/payment, installment, payment type, dia chi khach
- Target: order co ket thuc thanh cong bang delivered hay khong

### 3. Geo high-demand prediction

- Nguon: `fact_geo_daily`
- Dung cho: chon khu vuc marketing, chuan bi logistics, phan bo nguon luc
- Feature chinh: state/city, ngay/thang/thu, orders/revenue hien tai, review/SLA signal, lag va rolling average
- Target: khu vuc co nam trong nhom nhu cau cao 7 ngay tiep theo hay khong

## Phase de trien khai

| Phase | Noi dung |
| --- | --- |
| Phase 1 | Build core dims/facts cho BI |
| Phase 2 | Build aggregate facts: product/category/seller/geo daily |
| Phase 3 | Build 3 ML facts: product demand, order success, geo demand |
| Phase 4 | Train model tu `src/ml` va demo tren Streamlit |

## Ket luan

Thay vi duy tri 7+ bai toan ML va nhieu snapshot/prediction placeholder, datamart hien tai tap trung vao 3 use case de bao phu ba cau hoi lon:

- Ban cai gi? `product_bestseller`
- Don nao co kha nang thanh cong? `order_success`
- Ban o dau de hieu qua? `geo_high_demand`
