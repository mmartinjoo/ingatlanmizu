select
	count(*) as sold_listings,
	round(avg(days_on_market), 2) as average_days_on_market,
	percentile_cont(0.5) within group (order by days_on_market) as median_days_on_market
from {{ ref('int_listings__time_on_market') }}
where is_active is false