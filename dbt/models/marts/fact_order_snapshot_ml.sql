{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

select
    order_key,
    order_hashkey,
    customer_key,
    order_date_key as snapshot_date_key,
    order_purchase_timestamp::date as snapshot_date,
    order_status,
    total_items,
    distinct_products,
    distinct_sellers,
    total_item_price,
    total_freight_value,
    total_gross_amount,
    payment_transaction_count,
    distinct_payment_type_count,
    total_payment_value,
    max_payment_installments,
    has_installments,
    approval_lead_hours,
    approval_to_carrier_hours,
    delivery_cycle_days,
    is_delivered_late,
    review_count,
    avg_review_score,
    service_quality_band,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_orders') }}
