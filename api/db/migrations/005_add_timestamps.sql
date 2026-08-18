alter table bronze.zenga_listings
add column created_at timestamptz not null default now(),
add column updated_at timestamptz not null default now();

create or replace function bronze.set_updated_at()
returns trigger as $$
begin
    NEW.updated_at = now();
    return NEW;
end;
$$ language plpgsql;

create trigger zenga_listings_set_updated_at
before update on bronze.zenga_listings
for each row
execute function bronze.set_updated_at();