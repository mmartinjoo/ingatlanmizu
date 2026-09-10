# Data quality

[← Transformations](05-transformations.md) · [Docs index](README.md) · [Next: Operations →](07-operations.md)

---

Scraped data is wrong in ways that API data is not. Free-text fields contain typos, humans enter `"19"` for a construction year, the same concept appears under three spellings, and a source can change its markup overnight so that a selector starts returning empty strings instead of raising. None of those produce an error. They produce numbers.

The defence is four layers, ordered so that each catches what the one before it cannot.

Concretely, from the parsed dbt manifest: **15 models, 5 sources, and 183 data tests** — a little over twelve assertions per model.

| Layer | Mechanism | Catches |
|---|---|---|
| 1. Filter at the boundary | `where` clauses in staging | Values that are individually implausible |
| 2. Assert the grain | `unique_combination_of_columns` on every model | Joins that duplicated rows |
| 3. Bound the values | `not_null`, `not_empty`, `accepted_range`, `accepted_values` | Values that drifted out of the expected domain |
| 4. Monitor arrival | dbt source freshness | A pipeline that stopped working without failing |

The fourth is the one most projects skip, and the one that catches the failure mode scraping pipelines actually have.

## Layer 1 — filter at the boundary

From [`stg_zenga__listing_versions.sql`](../api/transform/models/staging/zenga/stg_zenga__listing_versions.sql):

```sql
from {{ source('bronze', 'zenga_listing_versions') }}
where ar is not null
and {{ hu_numeric('ar') }} != 0
and alapterulet is not null
-- typos like "7 m2"
and {{ hu_numeric('alapterulet') }} >= 10
and tipus is not null
and tipus not ilike '%villa%'
and tipus not ilike '%kastély%'
and tipus not ilike '%kúria%'
and tipus not ilike '%apartman%'
and (({{ hu_numeric('ar') }} * {{ price_magnitude('ar') }}) / {{ hu_numeric('alapterulet') }})
    between 10000 and 10000000
```

Every clause has a reason:

| Filter | Reason |
|---|---|
| `ar is not null`, `!= 0` | A listing with no price contributes nothing to a price statistic |
| `alapterulet >= 10` | Under 10 m² is not a dwelling. In practice these are typos — `"7 m2"` where 70 was meant. Keeping them puts an absurd price-per-m² into a median |
| `tipus is not null` | Type drives the `Ház` / `Lakás` split that every mart groups by |
| not villa / kastély / kúria / apartman | Castles, manor houses, villas and holiday apartments are not comparable housing stock. A handful of them in a rural county's sample moves that county's median more than the entire rest of the sample |
| price/m² between 10k and 10M HUF | An outlier band wide enough to include every genuine Hungarian property and narrow enough to exclude arithmetic that went wrong |

**These are modeling decisions, and they should be read as such.** Excluding villas is not objective — it is a choice about what "the market" means for this product, and a different product tracking luxury property would invert it. The 10k–10M band is a judgement call with defensible edges rather than a natural boundary.

The reason to filter in staging rather than in the marts is that it happens **once**, in one file, and every downstream model inherits it. Filtering per-mart guarantees the marts drift apart, and then two dashboards disagree and nobody knows which is right.

`bronze` keeps every excluded row. Filtering removes rows from the *analytical* layer, not from the record — so a decision made here can be revisited against the full history rather than requiring a re-crawl. That is the whole reason for keeping bronze faithful.

## Layer 2 — assert the grain

Every model declares what one row means, and dbt enforces it:

```yaml
models:
  - name: stg_zenga__listing_versions
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - listing_code
            - observed_at
```

Coverage, precisely — because "every model" would be an overstatement:

| Layer | Models with a declared grain |
|---|---|
| staging | `stg_zenga__listing_versions`, `stg_zenga__observations` — both |
| intermediate | all six: `int_listing_versions__unioned`, `int_observations__unioned`, `int_listings__current` (grain `listing_key`), `int_listings__price_changes`, `int_listings__time_on_market`, `int_listings__monthly` (grain `month_start` + `listing_key`) |
| marts | 3 of 7: `mart_listings_current`, `mart_market_monthly_by_county`, `mart_market_monthly_by_city` |

The four without one are `mart_average_time_on_market` — a single-row aggregate, where a grain assertion means nothing — `mart_market_indicators_monthly`, and the two month-over-month change marts. The last three are genuine gaps, and the change marts most of all: each joins a mart to a windowed version of itself on four columns, which is precisely the shape that fans out. Recorded in [Limitations](08-limitations.md).

This is the highest-value test in the project, for a reason worth spelling out: **grain violations are silent and they inflate.** A join that accidentally fans out one row into three does not error. It produces a `count(*)` that is 3× too high, and a median weighted toward whatever duplicated. The output looks entirely normal. Nothing else in the test suite catches it — `not_null` passes, ranges pass, the build is green — and the number is wrong.

Asserting the grain converts that class of bug from "discovered months later by someone who noticed a total looked high" into "the build fails on the commit that introduced it."

`int_listings__monthly` is where this matters most, since it is the one model joining two tables at different grains. Its grain assertion is what makes the `distinct on` provably correct rather than probably correct.

## Layer 3 — bound the values

### Ranges

```yaml
- name: price_per_square_meter
  data_tests:
    - not_null
    - dbt_utils.accepted_range:
        arguments:
          min_value: 10000
          max_value: 10000000
```

Ranges are declared on `price_huf`, `price_per_square_meter`, `area_sqm`, `year_of_building`, `max_number_of_floors_in_building`, `days_on_market`, `times_observed`, `condition_score`, and on the indicator sources — `apr` and `inflation` bounded to plausible percentages, `monthly_installment` to a sane forint range.

Note that `price_per_square_meter`'s range duplicates the staging filter. That is intentional belt-and-braces: the filter removes bad rows, the test asserts that the filter worked. If someone edits the `where` clause, the test fails rather than the bad data flowing through.

### Enumerations, with a deliberate severity split

```yaml
- name: main_type
  data_tests:
    - not_null
    - not_empty
    - accepted_values:
        values: ['Ház', 'Lakás']
        config:
          severity: error

- name: sub_type
  data_tests:
    - accepted_values:
        values: ['Ikerház', 'Házrész', 'Sorház', 'Családi ház', 'Lakás', ...]
        config:
          severity: warn
```

The rule: **error on what breaks a model, warn on what merely surprises you.**

`main_type` is `error` because every mart groups by it. An unrecognised value means listings falling out of aggregations or forming a phantom third category — a correctness failure, and the build should stop.

`sub_type` is `warn` because it is an open vocabulary. The source can add "Loft" tomorrow, and that is news, not breakage — it flows through as an ungrouped detail column and nothing downstream depends on the exact set. Failing the nightly build over it would be crying wolf, and a test suite that cries wolf gets ignored, which is worse than not having it.

Same logic elsewhere: `county` and `source` are `error` (they are join and grouping keys, and the county list is finite and known); `condition` is `warn` (open vocabulary, and `condition_score` already maps unknowns to a midpoint).

A test suite where everything is an error is a test suite people learn to override.

### `not_empty` — a custom test for a scraping-specific failure

[`tests/generic/not_empty.sql`](../api/transform/tests/generic/not_empty.sql):

```sql
{% test not_empty(model, column_name) %}
select *
from {{ model }}
where trim({{ column_name }}) = ''
{% endtest %}
```

Four lines, and it closes a real gap. `not_null` does not catch `''`, and HTML scraping produces empty strings *constantly* — `element.get_text()` on a node that rendered but has no content returns `''`, not `None`. An empty string then passes `not_null`, flows into a `group by`, and creates a phantom category with an empty label that nobody notices until it appears on a chart.

`_text()` in the parser already guards this with `or None` ([`parse.py`](../api/packages/ingest/src/ingatlanmizu/ingest/sources/zenga/parse.py)), but the test asserts the property independently of the code meant to maintain it — which is the correct relationship between a guard and a test.

It is applied to every text column that matters: `listing_code`, `listing_key`, `city`, `county`, `main_type`, `condition`, `source`, `location_detail`.

### Key format

```yaml
- name: listing_key
  data_tests:
    - dbt_expectations.expect_column_values_to_match_like_pattern:
        like_pattern: "zenga:%"
```

Asserts the surrogate key carries its source prefix. Cheap now; the thing that catches a mis-prefixed union when a second source arrives.

## Fail loud

The most compact statement of the philosophy is one line of SQL with a two-word comment, in `stg_zenga__listing_versions`:

```sql
case
    when tipus ilike '%ház%'    then 'Ház'
    when tipus ilike '%lakás%'  then 'Lakás'
    when tipus ilike '%garzon%' then 'Lakás'
    else null       -- this will cause a data test error
end as main_type
```

An unrecognised property type from the source could be handled three ways:

1. Default it to `'Ház'` — silent, and wrong forever.
2. Add an `'Egyéb'` (other) bucket — silent, and it grows without anyone looking at it.
3. Emit `NULL`, which the `not_null` test on `main_type` turns into a build failure.

Option 3 is chosen deliberately, and the comment says so. The build breaks, someone reads the failing rows, and either the mapping gets extended or the new type gets filtered. The system's response to an unknown is to stop and ask rather than to guess.

That is the same instinct as the KSH parser raising `ValueError` instead of returning `{}` ([Market indicators](04-indicators.md)) and as `_highlight_params` dropping unrecognised labels rather than putting them in the wrong column ([Ingestion](02-ingestion.md)). Consistently, across three layers written at different times, **the failure mode chosen is the loud one.**

## Layer 4 — freshness

From [`_zenga__sources.yml`](../api/transform/models/staging/zenga/_zenga__sources.yml):

```yaml
- name: zenga_listing_versions
  loaded_at_field: created_at
  freshness:
    warn_after:  {count: 2, period: day}
    error_after: {count: 7, period: day}
```

Declared on both bronze listing sources and checked with `make dbt-freshness`.

This layer exists because of how scraping pipelines actually die. They do not crash. The site changes its markup, or adds a bot check, or the seed URLs stop resolving — and the crawler runs happily every 6 hours, finds zero listings, writes zero rows, exits 0, and sends no alert. Every dashboard keeps working, showing last week's numbers. Every other test in this document passes, because tests validate the rows that exist and there simply are not any new ones.

Freshness is the only check that asks *"is data still arriving?"* rather than *"is the data that arrived correct?"* — and for a pipeline whose dependency is somebody else's website, that is the more likely question to need answering.

Two days to warn is about eight expected runs; seven days to error is decisive. Both thresholds are deliberately generous, because the sampling crawl means individual runs vary a lot in yield.

## What is not covered

Stated plainly, because the gaps matter as much as the coverage:

- **No tests on the Python.** `pytest` is a dev dependency; there are no test files. All quality enforcement is in dbt, which validates the warehouse and nothing upstream of it. The parsers — the most fragile code in the repository, and the easiest to test with saved HTML fixtures — have no test coverage at all.
- **No anomaly detection.** Nothing notices a 40% month-over-month median move, which would far more likely be a pipeline defect than a market event.
- **No row-count regression checks.** A run that ingests 5 listings instead of 500 passes every test, because the 5 are individually fine.
- **One model's tests are silently disabled.** `mart_average_time_on_market` declares its tests under `data_test:` rather than `data_tests:`, so dbt never picks them up. It is the only model in the project with **zero** tests attached in the compiled manifest — confirmed by parsing the project and counting tests per node.

All three are in [Limitations](08-limitations.md) with concrete fixes.

## Running the checks

```bash
make dbt-test        # every data test
make dbt-freshness   # source freshness only
make dbt-build       # run + test, stopping on failure
```

`dbt build` is the one that runs in production nightly. It interleaves models and their tests in dependency order, so a model whose tests fail does not have its dependents built on top of it — bad data stops where it is detected instead of propagating into `gold` and out through the API.

---

[← Transformations](05-transformations.md) · [Docs index](README.md) · [Next: Operations →](07-operations.md)
