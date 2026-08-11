with 
    source as (
        select * from {{ source('bronze', 'zenga_listings') }}
    ),

    versioned as (
        select 
            *,
            row_number() over (
                partition by hirdeteskod
                order by created_at desc, id desc
            ) as version_rank
        from source
    ),

    latest as (
        select * 
        from versioned
        where version_rank = 1
    ),

    renamed as (
        select
            megnevezes as title,
            ({{ hu_numeric('ar') }} * {{ price_magnitude('ar') }})::bigint as price_huf,
            (({{ hu_numeric('ar') }} * {{ price_magnitude('ar') }}) / {{ hu_numeric('alapterulet') }})::int as price_per_square_meter,
            {{ city_name('cim') }} as city,
            {{ location_detail('cim') }} as location_detail,
            {{ hu_numeric('alapterulet') }} as area_sqm,
            {{ hu_numeric('telek') }} as plot_size,
            {{ hu_numeric('emelet') }} as floor,
            emelet as floor_raw,
            {{ number_of_rooms('szobak_szama') }} as number_of_rooms,
            szobak_szama as number_of_rooms_raw,
            leiras as description,
            hirdeteskod as listing_code,
            allapot as condition,
            futes as heating,
            {{ hu_numeric('epites_eve') }} as year_of_building,
            {{ hu_numeric('terasz') }} as balcony_area,
            energetikai_besorolas as energy_rating,
            tipus as type,
            szintek_szama as max_number_of_floors_in_building,
            created_at as created_at,
            ingestion_run_id as ingestion_run_id,
            payload_hash as payload_hash,
            hirdeto_neve as seller_name,
            ingatlan_iroda_neve as real_estate_office_name
        from latest
    )

select * from renamed