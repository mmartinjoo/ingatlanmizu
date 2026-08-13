alter table bronze.zenga_listings
add ingestion_run_id integer references ops.ingestion_runs(id);