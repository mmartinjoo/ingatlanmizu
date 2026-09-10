# Known limitations and roadmap

[← Operations](07-operations.md) · [Docs index](README.md)

---

Every item below is a real defect or a real constraint in the code as it stands, found by reading it. They are ordered roughly by how much they affect the numbers the system publishes.

Two of them — items 3 and 6 — are outright bugs producing wrong output right now.

---

## 1. Discovery samples rather than crawls, and the sample is not random

**Where:** [`sources/zenga/__init__.py`](../api/packages/ingest/src/ingatlanmizu/ingest/sources/zenga/__init__.py), [`sources/zenga/extract.py`](../api/packages/ingest/src/ingatlanmizu/ingest/sources/zenga/extract.py)

Each run draws 2 of 84 seed URLs and one page in `1..30`:

```python
seed_urls=_random_urls(2)
url = f"{seed_url.url}?page={random.randint(1, 30)}"
```

Four defects compound here:

- **Page ordering is not random with respect to price.** The source sorts by its own default — recency, promotion, or relevance — so page 17 is not an unbiased draw from the category. The sampling frame is unknown and probably price-correlated.
- **Seeds are drawn with replacement.** `random.randint` can return the same index twice, so one run can crawl one category twice and another zero times. It also produces duplicate run items (see item 7).
- **Coverage is uneven.** Four runs a day over 84 seeds means an average seed is drawn roughly once every ten days, with high variance. Some counties go a week unsampled.
- **Fixed page ceiling.** `randint(1, 30)` assumes at least 30 pages exist. A small county has fewer, and those requests return an empty or error page rather than listings.

Everything downstream inherits this. `listing_count` is a count of *sampled* listings. The medians are medians of a convenience sample. Item 2 depends on it entirely.

**Fix:** replace the random draw with a persisted round-robin cursor over the 84 seeds so coverage is provably uniform; paginate each seed until exhausted rather than jumping to a random page; record the pages actually fetched in `ops.ingestion_runs.metadata` so the sampling frame is auditable per run. Full coverage of 84 categories is not a large crawl — it is well within a polite request budget at a 6-hourly cadence.

---

## 2. Time on market conflates disappearance with sale

**Where:** [`int_listings__time_on_market.sql`](../api/transform/models/intermediate/int_listings__time_on_market.sql), [`mart_average_time_on_market.sql`](../api/transform/models/marts/mart_average_time_on_market.sql)

```sql
select count(*) as sold_listings, round(avg(days_on_market), 2) as average_days_on_market, ...
from {{ ref('int_listings__time_on_market') }}
where is_active is false
```

The column is named `sold_listings`. What `is_active is false` actually means is *not seen recently*, and a listing stops being seen for at least four different reasons: it sold, it expired, the seller withdrew it, or — overwhelmingly the most common here — **the sampler did not draw its category again**.

Given item 1, most listings are observed once. `first_seen_at` equals `last_seen_at`, `days_on_market` is 1, and the three-day tolerance elapses within twelve runs. The mart therefore reports a large number of "sold" properties with an average time on market near one day, which describes the crawler's sampling interval and not the market.

The tolerance variable (`time_on_market_active_tolerance_days: 3`) is a mitigation for a much milder version of this problem — an occasional missed run — not for systematic undersampling.

**Fix:** item 1 first; this metric is not repairable without full coverage. In the interim, rename the column to `disappeared_listings`, and treat `days_on_market` as meaningful only for listings with `times_observed > 1`. Longer term, a listing that vanishes while an active crawl is covering its category is genuinely informative — that inference just needs the coverage to support it.

---

## 3. `base_rate` is wrong for every month but the current one

**Where:** [`mart_market_indicators_monthly.sql`](../api/transform/models/marts/mart_market_indicators_monthly.sql) — **active bug**

```sql
select
    date_trunc('month', available_at)::date as month_start,
    (
        select base_rate
        from {{ source('bronze', 'mnb_base_rates') }}
        order by valid_until desc
        limit 1
    ) as base_rate,
    ...
```

The subquery is uncorrelated: it references nothing in the outer query, so it evaluates once and returns the single most recent MNB base rate, which is then attached to **every** month in the table. A row describing last October reports today's base rate.

The irony is that the data needed to fix it already exists and was built specifically for this. [`mnb/parse.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/mnb/parse.py) goes to real trouble deriving `valid_from` / `valid_until` intervals from MNB's change-log ([Market indicators](04-indicators.md)), and this query ignores both columns.

**Fix:**

```sql
join {{ source('bronze', 'mnb_base_rates') }} as rates
    on date_trunc('month', loans.available_at)::date
       between rates.valid_from and rates.valid_until
```

and add `rates.base_rate` to the `group by`. A test would have caught this: `base_rate` currently has no assertion beyond source-level `not_null`, and a check requiring more than one distinct base rate across a multi-month table would fail today.

---

## 4. No retry, no backoff, no politeness controls

**Where:** [`sources/zenga/extract.py`](../api/packages/ingest/src/ingatlanmizu/ingest/sources/zenga/extract.py), [`runner.py`](../api/packages/ingest/src/ingatlanmizu/ingest/runner.py)

Every HTTP call is `resp.raise_for_status()` with a 30-second timeout and nothing else:

- A transient 503 or connection reset permanently fails that item for that run.
- Nothing ever re-drives `failed` items — no retry pass, no `retry_count` column, no dead-letter handling.
- No delay between requests. Eight threads fetch as fast as the source responds.
- No `robots.txt` check, and no `User-Agent` identifying the crawler or offering contact details.

The last two matter beyond data quality. The random sampling keeps total volume low, which is why this has not caused a problem — but low volume by accident is not the same as rate limiting by design.

**Fix:** wrap fetches in bounded retry with exponential backoff and jitter, retrying only on 5xx and connection errors and never on 404; add `retry_count` to `ops.ingestion_run_items` and a re-queue pass over `failed` items at the end of `extract_stage`; set a descriptive `User-Agent`; add a small inter-request delay; check `robots.txt` once per run.

---

## 5. A run where everything failed still reports success

**Where:** [`tracking.py`](../api/packages/ingest/src/ingatlanmizu/ingest/tracking.py), [`run.py`](../api/packages/ingest/src/ingatlanmizu/ingest/run.py)

```python
def finish_run(run_id: int) -> None:
    conn.execute("update ops.ingestion_runs set status = %s, completed_at = now() where id = %s",
                 ("completed", run_id))
```

`finish_run` writes `'completed'` unconditionally. It never looks at the run's items. `ops.ingestion_runs` tracks `discovered_count` but has no `completed_count` or `failed_count`, so nothing at the run level records outcomes.

Combined with per-item failure isolation ([Ingestion](02-ingestion.md)) — which catches every exception by design — the consequence is that a run in which all 300 items failed exits 0, is marked `completed`, and sends **no alert**, because Ofelia alerts on non-zero exit ([Operations](07-operations.md)).

This is the largest hole in the system's operational awareness. Per-item isolation is the right design; what is missing is the aggregate check on top of it.

**Fix:** add `completed_count` and `failed_count` to `ops.ingestion_runs`; have `finish_run` aggregate item statuses, write the counts, and set `'completed_with_errors'` past a failure-rate threshold; exit non-zero when that threshold is crossed, so Ofelia's alert path actually fires. A near-zero `discovered_count` deserves the same treatment — that is the classic silent-death signature of a crawler whose source changed its markup.

---

## 6. `original_price_huf` is not the original price

**Where:** [`mart_listings_current.sql`](../api/transform/models/marts/mart_listings_current.sql) — **active bug**

```sql
oldest_prices as (
    select listing_key, previous_price_huf as oldest_price
    from (
        select *, row_number() over (partition by listing_key order by observed_at desc) as rn
        from {{ ref('int_listings__price_changes') }}
    )
    where rn = 1
)
```

`order by observed_at desc` with `rn = 1` selects the **most recent** price change, then takes the price from immediately before it. For a listing that went 50M → 48M → 45M, `oldest_price` is 48M.

So `original_price_huf`, `price_delta_huf`, and `price_change_pct` all describe only the latest price step, while their names — and the CTE's own name — promise the cumulative move from the first advertised price. A listing discounted 10% over three cuts reports only the last one.

**Fix:** `order by observed_at asc, bronze_id asc`. The `bronze_id` tiebreaker matches the ordering used in `int_listings__current` and `int_listings__price_changes`, keeping the result deterministic.

---

## 7. `enqueue_run_items` is inefficient and does not deduplicate

**Where:** [`tracking.py`](../api/packages/ingest/src/ingatlanmizu/ingest/tracking.py)

```python
for listing in listings:
    conn.execute("update ops.ingestion_runs set discovered_count = %s where ...", (len(listings), run_id))
    conn.execute("insert into ops.ingestion_run_items (...) values (...)")
    source.record_observation(listing, run_id)
    conn.commit()
```

Three problems in six lines:

- **The `discovered_count` update is inside the loop.** It writes the same constant `len(listings)` N times — N−1 redundant `UPDATE`s per run.
- **A commit per listing.** N round-trips and N transactions where one would do.
- **No deduplication.** `discover` appends every matching `<a>` on the page, and listing pages repeat links — a card's title and its thumbnail both point at the listing. The same `external_id` therefore produces multiple run items *and* multiple observation rows for one run, which inflates `times_observed` in [`int_listings__time_on_market`](../api/transform/models/intermediate/int_listings__time_on_market.sql) and causes the same page to be fetched and stored more than once.

Duplicate observations narrowly escape the grain test on `(listing_key, observed_at)` only because each `INSERT` gets its own `now()`, differing by microseconds. That is luck, not design.

**Fix:** deduplicate on `external_id` in `discover` — `dict.fromkeys` preserves order, and the image handling in the same package already does exactly this — then use one `executemany` for the items, one for the observations, one `UPDATE` for the count, and one commit for the lot.

---

## 8. Some dbt tests are silently inactive, and three marts have no grain assertion

**Where:** [`mart_models.yml`](../api/transform/models/marts/mart_models.yml)

Two YAML typos disable real coverage:

```yaml
- name: mart_average_time_on_market
  columns:
    - name: sold_listings
      data_test:            # <- should be data_tests
        - not_null
        - dbt_utils.accepted_range:
          min_value: 0      # <- also mis-indented; should nest under arguments
          inclusive: true
```

`data_test:` is not a key dbt recognises, so none of that model's tests run. Parsing the project and counting tests per node confirms it: of 15 models carrying 183 tests between them, `mart_average_time_on_market` is the only one with **zero**. Every assertion on `mart_average_time_on_market` — the one mart whose semantics are already questionable (item 2) — is inert. The same file has `desciption:` on `mart_market_indicators_monthly`, so that model's description never reaches the docs site either.

Separately, three marts carry no `unique_combination_of_columns` grain assertion: `mart_market_indicators_monthly` and both month-over-month change marts. The change marts are the ones that matter, because each joins a mart to a windowed version of itself on four columns — exactly the shape that fans out silently ([Data quality](06-data-quality.md)).

**Fix:** correct both typos and fix the `arguments:` nesting; add grain tests on `(month_start, county, main_type)` and `(month_start, county, city, main_type)` for the change marts, and `(month_start)` for the indicators mart. These are the kind of mistake a schema linter or a CI step running `dbt parse --warn-error` catches immediately, which is another argument for item 11.

---

## 9. No tests on the Python

**Where:** the whole `api/packages` tree

`pytest` is declared in the `dev` dependency group. There are no test files.

All quality enforcement lives in dbt ([Data quality](06-data-quality.md)), which validates the warehouse and nothing upstream of it. That leaves the two most fragile pieces of code in the repository — the HTML parsers, whose correctness depends on someone else's markup — entirely uncovered, despite being the easiest things here to test: a saved HTML file in, an expected dict out, no infrastructure required.

**Fix, in priority order:**

1. Golden-file tests for [`zenga/parse.py`](../api/packages/ingest/src/ingatlanmizu/ingest/sources/zenga/parse.py) — fixtures for a flat, a house, one with a gated energy rating, one with missing highlight params. This is the highest-value test in the project, because it turns a markup change from a silent data-quality drift into a red build.
2. Unit tests for `hash_payload` — assert that changing `html_path` does *not* change the hash and that changing `ar` does. The entire versioning scheme rests on that exclusion list ([Change detection](03-change-detection.md)) and nothing currently protects it.
3. Golden-file tests for [`ksh/parse.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/ksh/parse.py), including the colspan-offset column lookup.
4. Unit tests for the MNB interval derivation, especially the `i == 0` open-ended case.

---

## 10. No structured logging

**Where:** everywhere

`print()` throughout. `LOG_LEVEL` is declared in [`Settings`](../api/packages/core/src/ingatlanmizu/core/config.py) and never read by anything.

There is no correlation between a log line and the run that produced it, no levels, and no machine-readable output. Debugging a failed run means querying `error_message` out of Postgres by hand — which works, and is more than most scrapers offer, but it means the *successful* path is unobservable. Questions like "how long did discovery take" or "which seed produced the most items" have no answer.

**Fix:** `structlog` with JSON output, `run_id` and `run_item_id` bound into the context so every line is attributable, honour `LOG_LEVEL`, and emit stage timings. That would also make the aggregate counts in item 5 nearly free to produce.

---

## 11. Operational gaps

**No CI.** `ruff` and `mypy` are installed as dev dependencies and nothing runs them. There is no CI workflow — nothing lints, type-checks, or (once item 9 lands) tests on push.

**Deployment has no rollback.** `rsync` of the working tree plus `docker compose up --build` ([Operations](07-operations.md)) means production runs whatever was on disk at deploy time, including uncommitted changes, with no build artifact and no tagged version to return to. `docker compose down` first also means a short outage on every deploy.

**Secrets in `.env`.** Mounted into containers and shared by every service through a YAML anchor. Adequate for a single-author project; not a model for anything with more than one operator.

**No backups.** Postgres and MinIO write to bind-mounted host directories with no snapshot, no retention policy, and no restore procedure. Given that the entire value of this system is accumulated history that **cannot be recreated** — a market snapshot not taken in August 2026 is gone permanently — this is arguably a bigger risk than anything else on this page.

---

## 12. Code hygiene

Small, individually trivial, listed because a documentation set that skips them is not being honest:

- [`core/run.py`](../api/packages/core/src/ingatlanmizu/core/run.py) imports `list_buckets` from `ingatlanmizu.ingest.storage`, which does not exist, and its `main()` prints a placeholder. `make runcore` fails at import. Dead scaffolding — delete it, and drop the `run` console script with it.
- Unused imports: `from re import S` in [`sources/base.py`](../api/packages/ingest/src/ingatlanmizu/ingest/sources/base.py), `from ast import main` in [`api/selectors.py`](../api/packages/api/src/ingatlanmizu/api/selectors.py). Both are IDE auto-import accidents, and both are things `ruff` catches on the first CI run.
- `settings.migrations_dir` is declared and never read; [`migrate.py`](../api/packages/core/src/ingatlanmizu/core/migrate.py) computes the path itself with `Path(__file__).resolve().parents[5]`, a fragile relative walk that breaks if the package layout moves. Use the setting.
- `dict[str, any]` appears in several signatures — that is the builtin `any()` function, not `typing.Any`. It type-checks as `Any` by accident and asserts nothing. `mypy` would flag it.
- dbt test arguments are written two ways across the YAML files: some `accepted_range` calls nest parameters under `arguments:`, some pass them directly, and `severity` is sometimes under `config:` and sometimes not. Both forms work in current dbt; the inconsistency is a small trap for whoever edits next.
- [`mart_market_monthly_by_county`](../api/transform/models/marts/mart_market_monthly_by_county.sql) wraps `median_year_of_building` in `coalesce(..., 0)`, so "no construction year known" is published as the year 0 — a sentinel a consumer will eventually plot. `NULL` would be the honest value.
- `mart_market_indicators_monthly` exposes the previous month's inflation in a column named simply `inflation` ([Transformations](05-transformations.md)). The lag is deliberate and correct; the name does not say so.
- `macros/floor.sql` is an empty file; the `floor` macro actually lives in `macros/hu_numeric.sql`.
- The `dbt` console script in the built virtualenv resolves to `dbt-core-experimental-parser` (dbt Fusion 2.0 preview), which does not support the Postgres adapter and exits with `InvalidConfig (dbt1005)`. `dbt-core` 1.12 and `dbt-postgres` 1.11 are both installed and parse the project correctly when invoked as `python -m dbt.cli.main`, so this is an entry-point collision rather than a project problem — but it means `make dbt-build` fails out of the box. Pin the dbt group to exclude the experimental parser, or invoke dbt-core's module directly in the Makefile.
- `.env.example` is missing 17 of the 29 variables `docker-compose.yml` interpolates — every port, the MinIO credentials, `SITE_ADDRESS`, all three schedules, and the SMTP alerting block. Copying it and running `make up` does not work, which makes the repository harder to start than it needs to be.

---

## Roadmap

Ordered by value per unit of effort.

**First — cheap fixes to published numbers.** Items 3 and 6 are single-line SQL corrections to output that is wrong today. Item 5 is perhaps thirty lines and closes the biggest observability hole. All three could land in an afternoon.

**Second — the foundation everything else rests on.** Item 1 (deterministic full coverage) gates item 2 and the credibility of every count in the marts. Item 4 (retry and politeness) becomes more important, not less, as coverage increases.

**Third — durability.** Backups (item 11) protect the one asset that cannot be rebuilt.

**Fourth — the safety net.** Item 9, starting with parser golden files and the `hash_payload` exclusion tests. Item 10 makes item 5 easier and everything else debuggable. CI (item 11) makes items 8, 9, and 12 self-enforcing.

**Then — the thing all of this was built for.** A second source. The union seam ([Transformations](05-transformations.md)) and the source-prefixed `listing_key` exist for exactly that, and adding a second portal is the real test of whether the abstraction earns its keep. It is deliberately last: a second source multiplies every problem above, and is worth adding after they are fixed rather than before.

---

[← Operations](07-operations.md) · [Docs index](README.md)
