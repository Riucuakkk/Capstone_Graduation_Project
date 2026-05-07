{{ config(materialized='table', tags=['mart', 'dim']) }}

select distinct
    payment_type as payment_type_key,
    payment_type,
    case
        when payment_type = 'credit_card' then 'card'
        when payment_type = 'debit_card' then 'card'
        when payment_type = 'voucher' then 'voucher'
        when payment_type = 'boleto' then 'cash_equivalent'
        else 'other'
    end as payment_group,
    current_timestamp as mart_load_timestamp
from {{ ref('v_stg_source_order_payments') }}
where payment_type is not null
