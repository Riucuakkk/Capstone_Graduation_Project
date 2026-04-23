{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

select
    fo.order_key as ml_sample_key,
    fo.order_key,
    fo.customer_key,
    fo.order_date_key,
    fo.order_purchase_timestamp::date as order_date,
    dc.customer_city,
    dc.customer_state,
    coalesce(fo.total_items, 0) as total_items,
    coalesce(fo.distinct_products, 0) as distinct_products,
    coalesce(fo.distinct_sellers, 0) as distinct_sellers,
    coalesce(fo.total_item_price, 0) as total_item_price,
    coalesce(fo.total_freight_value, 0) as total_freight_value,
    coalesce(fo.total_gross_amount, 0) as total_gross_amount,
    coalesce(fo.payment_transaction_count, 0) as payment_transaction_count,
    coalesce(fo.distinct_payment_type_count, 0) as distinct_payment_type_count,
    coalesce(fo.total_payment_value, 0) as total_payment_value,
    coalesce(fo.max_payment_installments, 0) as max_payment_installments,
    coalesce(fo.has_installments, false) as has_installments,
    coalesce(fo.uses_credit_card, false) as uses_credit_card,
    coalesce(fo.uses_voucher, false) as uses_voucher,
    coalesce(fo.dominant_payment_type, 'unknown') as dominant_payment_type,
    fo.approval_lead_hours,
    case
        when fo.is_delivered then true
        when fo.is_canceled or fo.is_unavailable then false
        else null
    end as is_successful_order,
    case
        when fo.is_delivered then 'successful'
        when fo.is_canceled or fo.is_unavailable then 'not_successful'
        else 'in_progress_or_unknown'
    end as order_success_label,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_orders') }} fo
left join {{ ref('dim_customers') }} dc
    on fo.customer_key = dc.customer_key
where fo.is_delivered or fo.is_canceled or fo.is_unavailable
