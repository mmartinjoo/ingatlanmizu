select 
    *, 
    'zenga' as source,
    concat('zenga', ':', listing_code) as listing_key,
    case
        when type ilike '%ház%' then    'Ház'
        else                            'Lakás'
    end as main_type,
    type as sub_type
from {{ ref('stg_zenga__listing_versions') }}