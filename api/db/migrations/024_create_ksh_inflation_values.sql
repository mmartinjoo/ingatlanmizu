create table if not exists bronze.ksh_inflation_values(
    id serial primary key,
    month_start date not null unique,
    inflation numeric(4,2) not null
);