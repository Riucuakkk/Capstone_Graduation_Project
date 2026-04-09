{{ config(materialized='table', tags=['mart', 'dim']) }}

select
    geolocation_zip_code_prefix as geography_key,
    geolocation_zip_code_prefix,
    geolocation_city,
    geolocation_state,
    avg(geolocation_lat) as avg_latitude,
    avg(geolocation_lng) as avg_longitude,
    count(*) as geolocation_point_count,
    current_timestamp as mart_load_timestamp
from {{ ref('v_stg_source_geolocation') }}
group by
    geolocation_zip_code_prefix,
    geolocation_city,
    geolocation_state
