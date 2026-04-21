{{ config(
    materialized='table',
    tags=['business_vault', 'pit'],
    pre_hook=[
        "create index if not exists idx_lnk_order_customer_pit on {{ ref('lnk_order_customer') }} (order_hashkey, source_event_date desc, load_timestamp desc)",
        "create index if not exists idx_sat_customer_identity_pit on {{ ref('sat_customer_identity') }} (customer_hashkey, source_event_date desc, load_timestamp desc)",
        "create index if not exists idx_sat_customer_address_pit on {{ ref('sat_customer_address') }} (customer_hashkey, source_event_date desc, load_timestamp desc)",
        "create index if not exists idx_sat_order_status_pit on {{ ref('sat_order_status') }} (order_hashkey, source_event_date desc, load_timestamp desc)",
        "create index if not exists idx_sat_order_timestamps_pit on {{ ref('sat_order_timestamps') }} (order_hashkey, source_event_date desc, load_timestamp desc)",
        "create index if not exists idx_hub_customer_pit on {{ ref('hub_customer') }} (customer_hashkey)"
    ]
) }}

with order_date_bounds as (
    select
        ho.order_hashkey,
        ho.business_key as order_id,
        min(sot.order_purchase_timestamp::date) as first_snapshot_date,
        max(order_events.event_date) as last_snapshot_date
    from {{ ref('hub_order') }} ho
    left join {{ ref('sat_order_timestamps') }} sot
        on ho.order_hashkey = sot.order_hashkey
    left join {{ ref('sat_order_status') }} sos
        on ho.order_hashkey = sos.order_hashkey
    left join lateral (
        values
            (sot.order_purchase_timestamp::date),
            (sot.order_approved_at::date),
            (sot.order_delivered_carrier_date::date),
            (sot.order_delivered_customer_date::date),
            (sot.order_estimated_delivery_date::date),
            (to_date(sos.source_event_date, 'YYYYMMDD'))
    ) as order_events(event_date)
        on order_events.event_date is not null
    group by
        ho.order_hashkey,
        ho.business_key
),
order_calendar as (
    select
        odb.order_hashkey,
        odb.order_id,
        aod.as_of_date_key,
        aod.as_of_date
    from order_date_bounds odb
    inner join {{ ref('as_of_date') }} aod
        on aod.as_of_date >= odb.first_snapshot_date
       and aod.as_of_date <= coalesce(odb.last_snapshot_date, odb.first_snapshot_date)
    where odb.first_snapshot_date is not null
),
pit_resolved as (
    select
        oc.order_hashkey,
        oc.order_id,
        oc.as_of_date_key,
        oc.as_of_date,
        lnk.customer_hashkey,
        hcu.business_key as customer_id,
        sci.customer_unique_id,
        sca.customer_zip_code_prefix,
        sca.customer_city,
        sca.customer_state,
        sos.order_status,
        sos.source_event_date as status_effective_at,
        sot.order_purchase_timestamp,
        sot.order_approved_at,
        sot.order_delivered_carrier_date,
        sot.order_delivered_customer_date,
        sot.order_estimated_delivery_date
    from order_calendar oc
    left join lateral (
        select
            loc.customer_hashkey
        from {{ ref('lnk_order_customer') }} loc
        where loc.order_hashkey = oc.order_hashkey
          and loc.source_event_date <= to_char(oc.as_of_date, 'YYYYMMDD')
        order by loc.source_event_date desc, loc.load_timestamp desc
        limit 1
    ) lnk on true
    left join {{ ref('hub_customer') }} hcu
        on lnk.customer_hashkey = hcu.customer_hashkey
    left join lateral (
        select
            sci.customer_unique_id
        from {{ ref('sat_customer_identity') }} sci
        where sci.customer_hashkey = lnk.customer_hashkey
          and sci.source_event_date <= to_char(oc.as_of_date, 'YYYYMMDD')
        order by sci.source_event_date desc, sci.load_timestamp desc
        limit 1
    ) sci on true
    left join lateral (
        select
            sca.customer_zip_code_prefix,
            sca.customer_city,
            sca.customer_state
        from {{ ref('sat_customer_address') }} sca
        where sca.customer_hashkey = lnk.customer_hashkey
          and sca.source_event_date <= to_char(oc.as_of_date, 'YYYYMMDD')
        order by sca.source_event_date desc, sca.load_timestamp desc
        limit 1
    ) sca on true
    left join lateral (
        select
            sos.order_status,
            sos.source_event_date
        from {{ ref('sat_order_status') }} sos
        where sos.order_hashkey = oc.order_hashkey
          and sos.source_event_date <= to_char(oc.as_of_date, 'YYYYMMDD')
        order by sos.source_event_date desc, sos.load_timestamp desc
        limit 1
    ) sos on true
    left join lateral (
        select
            sot.order_purchase_timestamp,
            sot.order_approved_at,
            sot.order_delivered_carrier_date,
            sot.order_delivered_customer_date,
            sot.order_estimated_delivery_date
        from {{ ref('sat_order_timestamps') }} sot
        where sot.order_hashkey = oc.order_hashkey
          and sot.source_event_date <= to_char(oc.as_of_date, 'YYYYMMDD')
        order by sot.source_event_date desc, sot.load_timestamp desc
        limit 1
    ) sot on true
)

select
    order_hashkey,
    order_id,
    as_of_date_key,
    as_of_date,
    customer_hashkey,
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    order_status,
    status_effective_at,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    case
        when order_approved_at is not null and order_purchase_timestamp is not null
            then extract(epoch from (order_approved_at - order_purchase_timestamp)) / 3600.0
    end as approval_lead_hours,
    case
        when order_delivered_customer_date is not null and order_purchase_timestamp is not null
            then extract(epoch from (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0
    end as delivery_cycle_days,
    case
        when order_delivered_customer_date is not null
             and order_estimated_delivery_date is not null
             and order_delivered_customer_date::date > order_estimated_delivery_date::date
            then true
        when order_delivered_customer_date is not null
             and order_estimated_delivery_date is not null
            then false
    end as is_delivered_late,
    current_timestamp as bv_load_timestamp
from pit_resolved
