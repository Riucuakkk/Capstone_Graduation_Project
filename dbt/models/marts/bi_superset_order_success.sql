{{ config(materialized='view', tags=['mart', 'bi', 'superset']) }}

select
    ml_sample_key,
    order_key,
    customer_key,
    order_date_key,
    order_date,
    coalesce(customer_city, 'unknown') as customer_city,
    coalesce(customer_state, 'unknown') as customer_state,
    coalesce(total_items, 0) as total_items,
    coalesce(distinct_products, 0) as distinct_products,
    coalesce(distinct_sellers, 0) as distinct_sellers,
    coalesce(total_item_price, 0) as item_value,
    coalesce(total_freight_value, 0) as freight_value,
    coalesce(total_gross_amount, 0) as gross_value,
    coalesce(payment_transaction_count, 0) as payment_transactions,
    coalesce(distinct_payment_type_count, 0) as payment_type_count,
    coalesce(total_payment_value, 0) as payment_value,
    coalesce(max_payment_installments, 0) as max_installments,
    case when has_installments then 1 else 0 end as installment_flag,
    case when uses_credit_card then 1 else 0 end as credit_card_flag,
    case when uses_voucher then 1 else 0 end as voucher_flag,
    coalesce(dominant_payment_type, 'unknown') as dominant_payment_type,
    approval_lead_hours,
    case when is_successful_order then 1 else 0 end as success_flag,
    case when is_successful_order then 0 else 1 end as not_successful_flag,
    case
        when is_successful_order then 'Successful delivered sale'
        else 'Canceled or unavailable'
    end as order_success_label,
    case
        when coalesce(total_payment_value, 0) >= 500 then 'high_value'
        when coalesce(total_payment_value, 0) >= 150 then 'medium_value'
        else 'low_value'
    end as order_value_band,
    case
        when has_installments then 'installment'
        else 'one_shot'
    end as installment_label,
    case
        when approval_lead_hours is null then 'unknown'
        when approval_lead_hours <= 1 then 'fast_approval'
        when approval_lead_hours <= 24 then 'same_day_approval'
        else 'slow_approval'
    end as approval_speed_band,
    case
        when coalesce(total_gross_amount, 0) > 0 then coalesce(total_freight_value, 0) / total_gross_amount
        else 0
    end as freight_to_gross_ratio
from {{ ref('fact_ml_order_success') }}
