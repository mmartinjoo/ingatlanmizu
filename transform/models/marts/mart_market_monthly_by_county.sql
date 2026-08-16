select
	listings.month_start as month_start,
	listings.county as county,
	listings.main_type as main_type,
	count(*) as listing_count,

	count(*) filter (where listings.is_new_build) as new_build_count,
	count(*) filter (where not listings.is_new_build) as old_build_count,
	count(*) filter (where listings.is_new_build is null) as unknown_build_count,
	
	percentile_cont(0.5) within group (
		order by listings.price_huf::numeric / nullif(listings.area_sqm, 0)
	)::int as median_price_per_sqm,
	
	percentile_cont(0.25) within group (
		order by listings.price_huf::numeric / nullif(listings.area_sqm, 0)
	)::int as p25_median_price_per_sqm,
	
	percentile_cont(0.75) within group (
		order by listings.price_huf::numeric / nullif(listings.area_sqm, 0)
	)::int as p75_median_price_per_sqm,

	coalesce(percentile_cont(0.5) within group (
		order by listings.year_of_building
	)::int, 0) as median_year_of_building,

	percentile_cont(0.5) within group (
		order by listings.condition_score
	)::int as median_condition_score,

	case
		when count(*) filter (where listings.is_new_build) = 0 		then null
		when count(*) filter (where not listings.is_new_build) = 0 	then null
		else round(
			(
				count(*) filter (where listings.is_new_build)::numeric
				/ 
				nullif((count(*) filter (where listings.is_new_build) + count(*) filter (where not listings.is_new_build)), 0)
			) * 100
		, 2) 
	end as new_build_ratio
	
from {{ ref('int_listings__monthly') }} as listings
where listings.price_huf is not null
and listings.area_sqm is not null
group by 1, 2, 3