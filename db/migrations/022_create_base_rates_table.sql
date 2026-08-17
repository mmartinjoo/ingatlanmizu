create table if not exists bronze.base_rates(
    valid_from datetime not null,
    valid_until datetime not null,
    value numeric(6, 2) not null
)