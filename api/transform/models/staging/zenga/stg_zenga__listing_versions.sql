with 
    source as (
        select * 
        from {{ source('bronze', 'zenga_listing_versions') }}
        where ar is not null
        and {{ hu_numeric('ar') }} != 0
        and alapterulet is not null
        -- typos like "7 m2"
        and {{ hu_numeric('alapterulet') }} >= 10
        and tipus is not null
        and tipus not ilike '%villa%'
        and tipus not ilike '%kastély%'
        and tipus not ilike '%kúria%'
        and tipus not ilike '%apartman%'
        and (({{ hu_numeric('ar') }} * {{ price_magnitude('ar') }}) / {{ hu_numeric('alapterulet') }})
            between 10000 and 10000000
    ),

    renamed as (
        select
            id as bronze_id,
            hirdeteskod as listing_code,
            {{ listing_key('zenga', 'hirdeteskod') }} as listing_key,
            'zenga' as source,
            megnevezes as title,
            ({{ hu_numeric('ar') }} * {{ price_magnitude('ar') }})::bigint as price_huf,
            (({{ hu_numeric('ar') }} * {{ price_magnitude('ar') }}) / {{ hu_numeric('alapterulet') }})::int as price_per_square_meter,
            {{ city_name('cim') }} as city,
            {{ location_detail('cim') }} as location_detail,
            {{ hu_numeric('alapterulet') }} as area_sqm,
            {{ hu_numeric('telek') }} as plot_size,
            {{ floor('emelet') }} as floor,
            emelet as floor_raw,
            {{ number_of_rooms('szobak_szama') }} as number_of_rooms,
            szobak_szama as number_of_rooms_raw,
            leiras as description,
            futes as heating,
            {{ year_of_building('epites_eve') }} as year_of_building,
            {{ hu_numeric('terasz') }} as balcony_area,
            -- JJ (2016-2023-as besorolás) -> JJ
            regexp_replace(energetikai_besorolas, '\s+\(.*', '') as energy_rating,            
            {{ hu_numeric('szintek_szama') }} as max_number_of_floors_in_building,
            created_at as observed_at,
            ingestion_run_id as ingestion_run_id,
            payload_hash as payload_hash,
            hirdeto_neve as seller_name,
            ingatlan_iroda_neve as real_estate_office_name,
            tipus as sub_type,
            megye as county,
            case
                when tipus ilike '%ház%'      then 'Ház'
                when tipus ilike '%lakás%'    then 'Lakás'
                when tipus ilike '%garzon%'   then 'Lakás'
                else null       -- this will cause a data test error
            end as main_type,
            case
                when allapot is null then   'Ismeretlen'
                when allapot = '' then      'Ismeretlen'
                else allapot
            end as condition
        from source
    )

select * from renamed