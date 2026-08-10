create table if not exists ops.ingestion_run_items (
    id serial primary key,

    ingestion_run_id integer not null,
    constraint fk_ingestion_run_items_ingestion_run
        foreign key (ingestion_run_id)
        references ops.ingestion_runs (id),

    external_id varchar(100) not null,
    url varchar(100) not null,
    status varchar(100) not null default 'pending',

    storage_folder text,
    content_hash text,
    error_message text,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create trigger ingestion_runs_items_set_updated_at
before update on ops.ingestion_run_items
for each row
execute function ops.set_updated_at();