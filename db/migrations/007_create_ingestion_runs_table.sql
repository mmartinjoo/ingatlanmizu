create table if not exists ops.ingestion_runs(
    id serial primary key,
    source varchar(100) not null,
    started_at timestamptz not null default now(),
    metadata jsonb,

    status varchar(50) not null default "running"

    discovered_count int not null default 0,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create or replace function ops.set_updated_at()
returns trigger as $$
begin
    NEW.updated_at = now();
    return NEW;
end;
$$ language plpgsql;

create trigger ingestion_runs_set_updated_at
before update on ops.ingestion_runs
for each row
execute function ops.set_updated_at();