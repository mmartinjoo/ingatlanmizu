with 
    source as (
        select * from {{ ref('stg_zenga__listing_versions') }}
    ),

    versioned as (
        select 
            *,
            row_number() over (
                partition by listing_code
                order by observed_at desc, bronze_id desc
            ) as version_rank
        from source
    )

select * from versioned where version_rank = 1