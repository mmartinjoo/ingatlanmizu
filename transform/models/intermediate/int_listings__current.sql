with 
    source as (
        select * from {{ ref('int_listing_versions__unioned') }}
    ),

    versioned as (
        select 
            *,
            row_number() over (
                partition by listing_key
                order by observed_at desc, bronze_id desc
            ) as version_rank
        from source
    )

select * from versioned where version_rank = 1