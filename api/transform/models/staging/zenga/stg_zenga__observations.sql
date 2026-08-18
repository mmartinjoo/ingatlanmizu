select 
    id as bronze_id,
    listing_code,
    observed_at,
    ingestion_run_id,
    {{ listing_key('zenga', 'listing_code') }} as listing_key,
    'zenga' as source
from {{ source('bronze', 'zenga_observations') }}