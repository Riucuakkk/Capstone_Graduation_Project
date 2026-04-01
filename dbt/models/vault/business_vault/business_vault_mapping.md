# Business Vault mapping for Olist dataset

## Muc tieu

Business Vault trong du an nay nen tap trung vao cac bang co gia tri truc tiep cho dashboard, forecast, machine learning va mart layer, thay vi mo rong tat ca pattern Data Vault.

## De xuat toi thieu can co

| Business Vault model | Grain | Nguon raw_vault | Business rule / gia tri them |
| --- | --- | --- | --- |
| `pit_order_snapshot` | 1 dong / order | `hub_order`, `lnk_order_customer`, `sat_order_status`, `sat_order_timestamps`, `sat_customer_identity`, `sat_customer_address` | Gom "latest state" cua order va customer de truy van nhanh, la diem vao chuan cho `fact_orders` |
| `bridge_order_line` | 1 dong / order item | `lnk_order_product_seller`, `sat_order_item_details`, `sat_product_details`, `sat_seller_address`, `pit_order_snapshot` | Enrich line item voi thong tin product, seller, delivery SLA, gross item amount |
| `bridge_order_payment` | 1 dong / order | `lnk_order_payment`, `sat_order_payment_details`, `hub_order` | Chuan hoa payment, tinh tong tien, dominant payment type, co installment hay khong |
| `bridge_customer_order` | 1 dong / customer | `pit_order_snapshot`, `bridge_order_payment`, `lnk_order_review`, `sat_review_details` | Customer 360 nhe cho `dim_customers`, retention/basic CLV, segmentation |

## Khong can uu tien ngay luc nay

| Model | Ly do chua can |
| --- | --- |
| PIT cho product/seller | Dataset Olist it bien dong theo thoi gian o hai entity nay, current snapshot la du |
| Bridge geolocation chi tiet | Can bo sung logic mapping zip/prefix phuc tap, nhung chua phai critical cho KPI cot loi |
| Multi-currency BV | Dataset co exchange rates, nhung giao dich Olist mac dinh BRL, co the them sau neu can tai chinh quoc te |

## Huong di tiep sang mart

| Mart huong toi | Nguon BV de dung |
| --- | --- |
| `mart.fact_orders` | `pit_order_snapshot` + `bridge_order_payment` |
| `mart.fact_order_items` | `bridge_order_line` |
| `mart.dim_customers` | `bridge_customer_order` |
| `mart.dim_products` | `bridge_order_line` tach distinct theo `product_id` |
| `mart.dim_sellers` | `bridge_order_line` tach distinct theo `seller_id` |
