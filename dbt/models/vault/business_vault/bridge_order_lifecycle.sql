{{ config(
    materialized='table',
    tags=['business_vault', 'order']
) }}

select
    pit.order_hashkey,
    pit.order_id,
    pit.customer_hashkey,
    pit.customer_id,
    pit.customer_unique_id,
    pit.order_status,
    pit.status_effective_at,
    pit.order_purchase_timestamp,
    pit.order_approved_at,
    pit.order_delivered_carrier_date,
    pit.order_delivered_customer_date,
    pit.order_estimated_delivery_date,
    pit.approval_lead_hours,
    pit.delivery_cycle_days,
    pit.is_delivered_late,
    (pit.order_approved_at is not null) as is_approved,
    (pit.order_delivered_carrier_date is not null) as is_shipped,
    (pit.order_delivered_customer_date is not null) as is_delivered,
    (pit.order_status = 'canceled') as is_canceled,
    (pit.order_status = 'unavailable') as is_unavailable,
    case
        when pit.order_delivered_carrier_date is not null and pit.order_approved_at is not null
            then extract(epoch from (pit.order_delivered_carrier_date - pit.order_approved_at)) / 3600.0
    end as approval_to_carrier_hours,
    case
        when pit.order_delivered_customer_date is not null and pit.order_delivered_carrier_date is not null
            then extract(epoch from (pit.order_delivered_customer_date - pit.order_delivered_carrier_date)) / 86400.0
    end as carrier_to_customer_days,
    case
        when pit.order_delivered_customer_date is not null and pit.order_estimated_delivery_date is not null
            then pit.order_delivered_customer_date::date - pit.order_estimated_delivery_date::date
    end as delivery_delay_days,
    current_timestamp as bv_load_timestamp
from {{ ref('bridge_order_current_snapshot') }} pit
