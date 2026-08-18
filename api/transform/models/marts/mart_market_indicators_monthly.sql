select
	date_trunc('month', available_at)::date as month_start,
	(
		select base_rate
		from {{ source('bronze', 'mnb_base_rates') }}
		order by valid_until desc
		limit 1
	) as base_rate,
	inflation.inflation,
	percentile_cont(0.5) within group(
		order by apr
	) as median_apr,
	min(apr) as lowest_apr,
	max(apr) as highest_apr,
	percentile_cont(0.5) within group(
		order by monthly_installment
	) as median_monthly_installment,
	min(monthly_installment) as lowest_monthly_installment,
	max(monthly_installment) as highest_monthly_installment
from {{ source('bronze', 'bankmonitor_loans') }} as loans
join {{ source('bronze', 'ksh_inflation_values') }} as inflation
	on inflation.month_start = date_trunc('month', loans.available_at)::date - interval '1 month'
group by 1, 2, 3