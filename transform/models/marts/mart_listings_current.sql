with 
	price_change_counts as (
		select 
			listing_key,
			count(listing_key) as price_changes_count
		from {{ ref('int_listings__price_changes') }}
		group by listing_key
	),
	
	oldest_prices as (
		select listing_key, previous_price_huf as oldest_price
		from {{ ref('int_listings__price_changes') }}
		order by observed_at asc
		limit 1
	)
	
select 
	listings.*,
	price_change_counts.price_changes_count,
	oldest_prices.oldest_price as original_price_huf,
	oldest_prices.oldest_price - price_huf as price_delta_huf,
	round(
		((oldest_prices.oldest_price - price_huf)::numeric / oldest_prices.oldest_price)*100, 
		2
	) as price_change_pct
from {{ ref('int_listings__current') }} as listings
left join price_change_counts
on listings.listing_key = price_change_counts.listing_key
left join oldest_prices
on listings.listing_key = oldest_prices.listing_key
