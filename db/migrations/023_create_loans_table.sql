create table if not exists bronze.loans(
    id serial primary key,
    name text default null,
    bank_name text not null,
    available_at date not null,    
    apr numeric(6,2) not null,
    monthly_installment int not null,
    full_payable_amount int not null
);