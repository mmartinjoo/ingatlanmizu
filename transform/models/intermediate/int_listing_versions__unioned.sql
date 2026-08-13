select 
    *
from {{ ref('stg_zenga__listing_versions') }}
where main_type != 'Villa, kastély'