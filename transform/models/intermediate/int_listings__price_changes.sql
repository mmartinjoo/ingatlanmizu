with versions as (
    select * from {{ ref('int_listing_versions__unioned') }}
),

with_previous as (
    select
        listing_key,
        observed_at,
        price_huf,
        lag(price_huf) over (
            partition by listing_key
            order by observed_at, bronze_id
        ) as previous_price_huf
    from versions
)

select
    listing_key,
    observed_at,
    previous_price_huf,
    price_huf as new_price_huf,
    price_huf - previous_price_huf as price_delta_huf,
    round(
        ((price_huf - previous_price_huf)::numeric / previous_price_huf) * 100,
        2
    ) as price_change_pct
from with_previous
where previous_price_huf is not null
and price_huf is distinct from previous_price_huf