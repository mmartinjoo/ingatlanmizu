with 
    source as (
        select * from {{ ref('stg_zenga__listing_versions') }}
    ),

    versioned as (
        select 
            *,
            row_number() over (
                partition by listing_code
                order by created_at desc, id desc
            ) as version_rank
        from source
    )

select * from versioned where version_rank = 1