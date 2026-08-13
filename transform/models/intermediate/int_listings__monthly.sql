with listing_months as (
    select distinct
        listing_key,
        date_trunc('month', observed_at)::date as month_start
    from {{ ref('int_observations__unioned') }}
)

select distinct on (listing_months.listing_key, listing_months.month_start)
    listing_months.month_start,
    listing_months.listing_key,
    versions.county,
    versions.city,
    versions.main_type,
    versions.sub_type,
    versions.price_huf,
    versions.area_sqm
from listing_months
join {{ ref('int_listing_versions__unioned') }} as versions
    on versions.listing_key = listing_months.listing_key
    and versions.observed_at < listing_months.month_start + interval '1 month'
order by
    listing_months.listing_key,
    listing_months.month_start,
    versions.observed_at desc,
    versions.bronze_id desc