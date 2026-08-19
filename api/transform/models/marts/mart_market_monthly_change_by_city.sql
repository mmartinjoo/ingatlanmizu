with 
	previous as (
		select
			month_start,
			county,
			city,
			main_type,
			lag(median_price_per_sqm) over (
				partition by county, city, main_type
				order by month_start
			) as median_price_per_sqm
		from {{ ref('mart_market_monthly_by_city') }}
	)

select 
	current.month_start,
	current.county,
	current.city,
	current.main_type,
	current.median_price_per_sqm as current_median_price_per_sqm,
	previous.median_price_per_sqm as previous_median_price_per_sqm,
	round(((current.median_price_per_sqm - previous.median_price_per_sqm)::numeric / current.median_price_per_sqm)*100, 2) as change_pct
from {{ ref('mart_market_monthly_by_city') }} as current
join previous
	on current.month_start = previous.month_start
	and current.county = previous.county
	and current.city = previous.city
	and current.main_type = previous.main_type