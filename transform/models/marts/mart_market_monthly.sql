select
	date_trunc('month', observed_at)::date as month_start,
	city,
	main_type,
	sub_type,
	count(distinct listing_key) as listing_count,
	
	percentile_cont(0.5) within group (
		order by price_huf::numeric / nullif(area_sqm, 0)
	)::int as median_price_per_sqm,
	
	percentile_cont(0.25) within group (
		order by price_huf::numeric / nullif(area_sqm, 0)
	)::int as p25_median_price_per_sqm,
	
	percentile_cont(0.75) within group (
		order by price_huf::numeric / nullif(area_sqm, 0)
	)::int as p75_median_price_per_sqm
	
from {{ ref('int_listings__unioned') }}
where price_huf is not null
and area_sqm is not null
group by 1, 2, 3, 4