create table if not exists bronze.mnb_base_rates(
    id serial primary key,
    valid_from date not null,
    valid_until date not null,
    base_rate numeric(6, 2) not null
);

create unique index valid_from_valid_until_unique on bronze.mnb_base_rates(valid_from, valid_until);