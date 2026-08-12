create table if not exists bronze.zenga_observations (
    id serial primary key,
    listing_code varchar(100) not null,
    observed_at timestamptz default now(),
    ingestion_run_id int references ops.ingestion_runs (id)
)