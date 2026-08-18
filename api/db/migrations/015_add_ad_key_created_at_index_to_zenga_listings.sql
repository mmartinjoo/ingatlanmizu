create index if not exists idx_zenga_hirdeteskod_created_at
on bronze.zenga_listings (hirdeteskod, created_at desc);