{{ config(
    materialized='table',
    tags=['business_vault', 'pit']
) }}

with current_snapshot as {{ latest_by_key(
    'pit_order_snapshot',
    'order_hashkey',
    [
        'order_id',
        'as_of_date_key',
        'as_of_date',
        'customer_hashkey',
        'customer_id',
        'customer_unique_id',
        'customer_zip_code_prefix',
        'customer_city',
        'customer_state',
        'order_status',
        'status_effective_at',
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
        'approval_lead_hours',
        'delivery_cycle_days',
        'is_delivered_late',
        'bv_load_timestamp'
    ],
    'as_of_date desc, bv_load_timestamp desc'
) }}

select *
from current_snapshot
