# Market indicators

[← Change detection](03-change-detection.md) · [Docs index](README.md) · [Next: Transformations →](05-transformations.md)

---

A price per square metre is not, on its own, an answer to any question a person actually has. "Is this expensive?" needs inflation. "Can I afford it?" needs mortgage rates. "Is now a bad time to buy?" needs both, plus the central bank's direction of travel.

The `indicators` package ([`packages/indicators`](../api/packages/indicators/src/ingatlanmizu/indicators/)) collects those three series. It is a useful counterpart to the listings crawl because it demonstrates the same principles against three sources that could hardly be less alike — a spreadsheet, an undocumented JSON API, and a government statistical table — and because **each one needs a different idempotency strategy**, chosen from the shape of the data rather than applied uniformly.

The entry point is flat and deliberately boring ([`run.py`](../api/packages/indicators/src/ingatlanmizu/indicators/run.py)):

```python
def main():
    _ingest_bankmonitor_loans()
    _ingest_mnb_base_rates()
    _ingest_ksh_inflation()
```

Each is a `fetch → parse → load` triple, the same decomposition the listings source uses, without the run tracking and threading — because there is nothing here to track or parallelise. Three requests, three files, three loads. Machinery proportionate to the job.

## Four sources, four refresh strategies

This table is the point of the document.

| Source | Shape | Refresh strategy | Why this one |
|---|---|---|---|
| **MNB** base rate | Complete change-log, a few dozen rows | `truncate ... restart identity` then reload | The source is authoritative and complete on every fetch. Rebuilding is cheaper and safer than diffing |
| **Bankmonitor** offers | Daily snapshot, ~10 rows per day | Delete-then-insert on `(name, bank_name, available_at)` | Natural key exists. Re-running the same day must overwrite, not duplicate |
| **KSH** inflation | Monthly series, published late, revised | Insert only if no non-null value exists for that month | Late publication means most months are `null` on any given fetch. Never overwrite a captured value with a later blank |
| **zenga** listings | Continuous, high volume, history *is* the product | Append a version only if the payload hash differs | Covered in [Change detection](03-change-detection.md) |

The general rule: **idempotency strategy is a property of the source's publication behaviour, not a house style.** Applying truncate-and-reload to KSH would discard captured months whenever KSH republished a page with blanks. Applying insert-if-absent to MNB would miss the corrections MNB occasionally issues. Each is right for one source and wrong for the others.

All four also write their raw artifact to object storage before parsing ([`storage.py`](../api/packages/indicators/src/ingatlanmizu/indicators/storage.py)) — the same raw-first principle as the listings crawl, for the same reason.

## MNB — turning a change-log into validity intervals

The Hungarian National Bank publishes its base rate history as an `.xlsx` at a stable URL. Acquisition is four lines of `requests` plus `pandas.read_excel` ([`mnb/extract.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/mnb/extract.py)).

The interesting part is the modeling. The source has two columns — a date the rate took effect, and the rate — with newest first. It is a **change-log**: it says when things changed, not what was true when.

Almost every consumer needs the opposite. `mart_market_indicators_monthly` wants the rate in effect during a given month, which requires each row to carry a validity *interval*, not just a start. [`mnb/parse.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/mnb/parse.py) derives it:

```python
for i in range(len(values)-1, -1, -1):
    if i == 0:
        valid_until = datetime.now() + timedelta(days=90)
    else:
        valid_until = values[i-1] - timedelta(days=1)
    df_renamed.at[i, "valid_until"] = valid_until.strftime("%Y-%m-%d")
```

Walking from oldest to newest, each row's validity ends the day before the next one begins — the standard change-log-to-interval conversion, closing each period against its successor.

Row 0 is the current rate, which has no successor. It is given `now() + 90 days`: an interval that has to be *open* to be usable in a `between` join, but must not be infinite, because an unbounded end date would let a stale value silently answer queries about dates long after the pipeline stopped running. Ninety days is a bet that the job will run again within a quarter, and a value that starts returning no rows if it does not. Failing to a gap is better than failing to a wrong number.

The rest of the parser handles Hungarian formatting: `"6,50%"` → `6.50` via `%` strip and comma-to-dot. Column names are also renamed out of Hungarian at this point, so the loader deals in `valid_from` / `valid_until` / `base_rate`.

Loading is a full replace ([`mnb/load.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/mnb/load.py)):

```python
conn.execute("truncate table bronze.mnb_base_rates restart identity")
```

Justified because the fetched file is the complete history, every time, and it is a few dozen rows. Diffing would be more code and more failure modes for a table that rebuilds in milliseconds. `restart identity` resets the sequence so IDs stay dense rather than climbing forever across rebuilds.

The uniqueness of `(valid_from, valid_until)` is enforced in the schema ([migration 022](../api/db/migrations/022_create_mnb_base_rates_table.sql)) rather than assumed by the loader — so a source file with overlapping or repeated periods fails the load instead of producing a table where a `between` join silently returns two rows.

*What it costs:* truncate-and-reload is not concurrency-safe. A query landing mid-load sees an empty table. With one nightly writer and no long-running readers this is not a live risk, but it is the reason this strategy does not generalise.

## Bankmonitor — a request body as methodology

[`bankmonitor/extract.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/bankmonitor/extract.py) POSTs to an undocumented public endpoint with a ~60-field JSON body. At a glance it reads as copied-from-devtools boilerplate. It is not — it is the **definition of the measurement**, and it is the most consequential decision in this package.

The body pins a *reference borrower*:

| Parameter | Value |
|---|---|
| Loan goal | `HASZNALT_LAKAS` — existing (not new-build) home |
| Loan amount | 40,000,000 HUF |
| Property value | 60,000,000 HUF (so a 67% loan-to-value) |
| Term | 20 years |
| Applicant | Age 29, 1,000,000 HUF monthly salaried income |
| Property type | Brick or Ytong flat |
| Banks | 10 named: CIB, Duna, Erste, Gránit, K&H, MBH, MagNet, OTP, Raiffeisen, UniCredit |
| Ranked by | `THM` — the Hungarian statutory APR, which includes fees |
| Interest period | `FULL` — fixed for the whole term |

Mortgage pricing depends on the borrower as much as on the market: change the LTV, the term, or the income and every number moves. A series built from varying inputs measures the inputs, not the market.

Holding all of them fixed means the only thing that can move the series over time is bank pricing. That is what makes the resulting numbers a *market indicator* rather than a quote — and it is why the sprawling literal body is a feature. Every field in it is a variable being deliberately controlled.

Two consequences worth stating, since a fixed persona is a modeling choice with edges:

- The series measures the market **as seen by that borrower**. A first-time buyer with a 90% LTV faces different pricing; this series does not describe them.
- `onePerBank: True` takes each bank's best qualifying offer, so the sample is one offer per bank rather than a full product catalogue — which is what makes the median across banks meaningful.

Ranking by THM rather than nominal interest is the right call for the same reason: THM is legally required to include fees, so it compares products whose fee structures differ, which nominal rates do not.

Parsing is trivial ([`bankmonitor/parse.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/bankmonitor/parse.py)) — pull `name`, `bank.name`, `apr` (scaled from fraction to percent), `installmentStart`, `fullPayableAmount`, and stamp today's date as `available_at`.

Loading is delete-then-insert per row ([`bankmonitor/load.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/bankmonitor/load.py)):

```sql
delete from bronze.bankmonitor_loans
where name = %s and bank_name = %s and available_at = %s;

insert into bronze.bankmonitor_loans(...) values (...);
```

`(name, bank_name, available_at)` is the natural key: one product, one bank, one day. Running the job twice in a day replaces the earlier snapshot instead of duplicating it — a manual upsert, and the correct semantics for daily snapshot data.

*What it costs:* the delete-then-insert pair is a manual `ON CONFLICT`, and the key is not enforced by a unique constraint in the schema ([migration 023](../api/db/migrations/023_create_bankmonitor_loans_table.sql)), so correctness depends on the loader rather than on the database. A unique index on those three columns plus `insert ... on conflict do update` would push the guarantee down to where it cannot be bypassed.

## KSH — the defensive parser

The Central Statistical Office publishes inflation as a STADAT HTML page. No API, no CSV — a table in a document that exists to be read by humans, and whose structure is not a stable contract.

[`ksh/parse.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/ksh/parse.py) is the most defensive code in the repository, and every piece of that defensiveness is aimed at one failure mode: **reading the wrong number and not noticing.**

**Find the table section by its heading text, not by position.** The page carries several `<tbody>` groups — year-on-year, month-on-month, index values:

```python
def _find_group(soup):
    for tbody in soup.find_all("tbody"):
        heading = tbody.find("tr")
        if heading and _normalize(_clean(heading)) == _normalize(GROUP_HEADING):
            return tbody
    raise ValueError(f"Group not found on the page: {GROUP_HEADING!r}")
```

`GROUP_HEADING` is `"Az előző év azonos időszaka = 100,0%"` — same period of the previous year = 100%, i.e. year-on-year change. Taking the second `<tbody>` instead would work until KSH added a section, at which point the pipeline would silently start reporting month-on-month figures as if they were annual.

**Find the column by walking `colspan`.** The header has merged cells, so a column's visual position is not its cell index:

```python
def _total_column_index(table) -> int:
    header_row = table.find("thead").find_all("tr")[-1]
    position = 0
    for cell in header_row.find_all(["th", "td"]):
        span = int(cell.get("colspan", 1))
        if _clean(cell) == TOTAL_COLUMN:
            return position
        position += span
    raise ValueError(f"Column not found in the table header: {TOTAL_COLUMN!r}")
```

Accumulating `colspan` computes where the `"Összesen"` (total) column actually starts. A hard-coded index would be off by however many merged cells precede it, and would drift the moment KSH adds a category.

**Normalise the typography.** Published HTML tables are full of characters that break naive parsing:

```python
def _clean(cell) -> str:
    cell = cell.__copy__()
    for sup in cell.find_all("sup"):
        sup.decompose()
    return cell.get_text(strip=True).replace("\xa0", "").replace("\u2009", "")
```

Footnote markers (`<sup>`) are removed on a *copy* of the node, so the parse is non-destructive; non-breaking (`\xa0`) and thin (`\u2009`) spaces — used as digit group separators — are stripped so `float()` sees a plain number.

**Treat the source's null markers as null.** `".."`, `"…"`, `"-"`, and `"–"` all mean "no data" in KSH tables, and all parse as garbage or raise if fed to `float()`. `_to_float` maps them to `None`.

**Convert index to change.** KSH publishes an index where the base period is 100. `103.5` means 3.5% inflation:

```python
result[f"{year}-{month:02d}-01"] = round(value - 100, 1) if value is not None else None
```

**Raise rather than return empty.** If no rows for the requested year are found, the parser raises `ValueError(f"No rows found for year {year}")`. This is the fail-loud principle: a parser that returns `{}` when the page structure changed produces a pipeline that runs green forever while the data quietly stops arriving. A raise sends an Ofelia alert email ([Operations](07-operations.md)).

Loading is insert-if-absent ([`ksh/load.py`](../api/packages/indicators/src/ingatlanmizu/indicators/sources/ksh/load.py)):

```python
row = conn.execute("""
    select exists (
        select 1 from bronze.ksh_inflation_values
        where month_start = %s and inflation is not null
    )
""", (month_start,)).fetchone()

if row[0]:
    continue
```

The parser returns all twelve months of the year, most of them `None` because they have not been published yet. `None` values are skipped, and a month that already holds a non-null value is never rewritten. The result is that each month's figure is captured once, on the first fetch after KSH publishes it, and is then stable.

*What it costs:* KSH does issue revisions, and this loader ignores them — first value wins, permanently. For a headline CPI that moves by tenths on revision, stability is arguably worth more than the correction; for a series where revisions are material, this would be the wrong choice. Either way it is a decision, and it should be a visible one.

## Where these land

All three write to `bronze`, and all three are consumed by [`mart_market_indicators_monthly`](../api/transform/models/marts/mart_market_indicators_monthly.sql) — which joins loan offers to inflation and the base rate to produce one row per month of affordability context. That mart is described in [Transformations](05-transformations.md), including a known defect in how it selects the base rate.

Unlike the listings sources, these three have **no staging models**. The marts read `source('bronze', ...)` directly. That is a deliberate shortcut for tables that are already clean, typed, and narrow — there is nothing for a staging layer to rename or cast. It is also the one place where the medallion layering is not strictly applied, which is worth knowing before someone assumes uniformity and looks for a `stg_mnb__base_rates` that does not exist.

The source-level dbt tests still apply — `not_null` and `accepted_range` on all three, defined in [`_mnb_sources.yml`](../api/transform/models/staging/mnb/_mnb_sources.yml), [`_bankmonitor_sources.yml`](../api/transform/models/staging/bankmonitor/_bankmonitor_sources.yml), and [`_ksh_sources.yml`](../api/transform/models/staging/ksh/_ksh_sources.yml). Skipping the staging *models* did not mean skipping the contracts.

---

[← Change detection](03-change-detection.md) · [Docs index](README.md) · [Next: Transformations →](05-transformations.md)
