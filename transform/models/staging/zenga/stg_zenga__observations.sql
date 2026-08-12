select 
    id as bronze_id,
    listing_code,
    observed_at,
    ingestion_run_id
from {{ source('bronze', 'zenga_observations') }}