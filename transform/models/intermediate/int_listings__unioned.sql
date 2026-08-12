select 
    *, 
    'zenga' as source,
    concat('zenga', ':', listing_code) as listing_key
from {{ ref('stg_zenga__listing_versions') }}