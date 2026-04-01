{{ config(
    materialized='table',
    tags=['business_vault', 'bridge']
) }}

with latest_payment_details as {{ latest_by_key(
    'sat_order_payment_details',
    'order_payment_hashkey',
    ['payment_type', 'payment_installments', 'payment_value']
) }},
payment_lines as (
    select
        op.order_hashkey,
        opd.payment_type,
        opd.payment_installments,
        opd.payment_value
    from {{ ref('lnk_order_payment') }} op
    left join latest_payment_details opd
        on op.order_payment_hashkey = opd.order_payment_hashkey
),
payment_type_ranked as (
    select
        order_hashkey,
        payment_type,
        sum(payment_value) as payment_type_value,
        row_number() over (
            partition by order_hashkey
            order by sum(payment_value) desc, payment_type
        ) as rn
    from payment_lines
    group by order_hashkey, payment_type
)

select
    pl.order_hashkey,
    ho.business_key as order_id,
    count(*) as payment_transaction_count,
    count(distinct pl.payment_type) as distinct_payment_type_count,
    sum(pl.payment_value) as total_payment_value,
    avg(pl.payment_value) as avg_payment_value,
    max(pl.payment_installments) as max_payment_installments,
    max(case when pl.payment_installments > 1 then 1 else 0 end) = 1 as has_installments,
    max(case when pl.payment_type = 'credit_card' then 1 else 0 end) = 1 as uses_credit_card,
    max(case when pl.payment_type = 'voucher' then 1 else 0 end) = 1 as uses_voucher,
    ptr.payment_type as dominant_payment_type,
    current_timestamp as bv_load_timestamp
from payment_lines pl
left join {{ ref('hub_order') }} ho
    on pl.order_hashkey = ho.order_hashkey
left join payment_type_ranked ptr
    on pl.order_hashkey = ptr.order_hashkey
   and ptr.rn = 1
group by
    pl.order_hashkey,
    ho.business_key,
    ptr.payment_type
