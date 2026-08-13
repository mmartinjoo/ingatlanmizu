select
	listings.month_start as month_start,
	listings.city as city,
	listings.main_type as main_type,
	listings.sub_type as sub_type,
	count(*) as listing_count,
	
	percentile_cont(0.5) within group (
		order by listings.price_huf::numeric / nullif(listings.area_sqm, 0)
	)::int as median_price_per_sqm,
	
	percentile_cont(0.25) within group (
		order by listings.price_huf::numeric / nullif(listings.area_sqm, 0)
	)::int as p25_median_price_per_sqm,
	
	percentile_cont(0.75) within group (
		order by listings.price_huf::numeric / nullif(listings.area_sqm, 0)
	)::int as p75_median_price_per_sqm
	
from {{ ref('int_listings__monthly') }} as listings
where listings.price_huf is not null
and listings.area_sqm is not null
group by 1, 2, 3, 4