with 
	observations as (
		select * from {{ ref('int_observations__unioned') }}
	),
	
	source_observations as (
		select 
			source,
			min(observed_at)::date as source_first_observed_at, 
			max(observed_at)::date as source_last_observed_at
		from observations
		group by source
	),
	
	times_seen as (
		select
			listing_key,
			source,
			min(observed_at)::date as first_seen_at, 
			max(observed_at)::date as last_seen_at,
			count(ingestion_run_id) times_observed
		from observations
		group by listing_key, source
	)
	
select
    times_seen.listing_key,
    times_seen.source,
    times_seen.first_seen_at,
	times_seen.last_seen_at,
    times_seen.times_observed,
	(times_seen.last_seen_at - times_seen.first_seen_at) + 1 as days_on_market,
	times_seen.last_seen_at >= source_observations.source_last_observed_at - {{ var('time_on_market_active_tolerance_days') }} as is_active
from times_seen
join source_observations 
on times_seen.source = source_observations.source