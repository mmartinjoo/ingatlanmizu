# Operations

[← Data quality](06-data-quality.md) · [Docs index](README.md) · [Next: Limitations →](08-limitations.md)

---

Everything here follows one rule: **infrastructure proportionate to the workload.** Three scheduled jobs on one machine do not need a distributed scheduler, and a hand-authored SQL schema does not need a migration framework. Each choice below is stated with what it gives up.

## Scheduling

Ofelia reads its job definitions from Docker labels on the `scheduler` service ([`docker-compose.yml`](../docker-compose.yml)):

```yaml
scheduler:
  command: sh -c "./wait-for-it.sh postgres:5432 -t 30 && ./wait-for-it.sh minio:9000 -t 30 && sleep infinity"
  labels:
    ofelia.enabled: "true"
    ofelia.job-exec.ingest.schedule: ${INGESTION_SCHEDULE}
    ofelia.job-exec.ingest.command: "make runingest"
    ofelia.job-exec.transform.schedule: ${TRANSFORM_SCHEDULE}
    ofelia.job-exec.transform.command: "make dbt-build"
    ofelia.job-exec.indicators.schedule: ${INDICATORS_SCHEDULE}
    ofelia.job-exec.indicators.command: "make runindicators"
```

| Job | Schedule | Command |
|---|---|---|
| `ingest` | `@every 6h` | `make runingest` — crawl zenga.hu |
| `indicators` | `@midnight` | `make runindicators` — MNB, Bankmonitor, KSH |
| `transform` | `@midnight` | `make dbt-build` — rebuild silver and gold, with tests |

The `scheduler` container does nothing itself — `sleep infinity` after waiting for Postgres and MinIO to accept connections. Ofelia's `job-exec` runs each command *inside* that already-running container.

That indirection is the point. Jobs execute in the same image, with the same dependencies, the same environment variables, and the same mounted code as the API. There is no separate worker image to keep in sync, and no class of bug where a job works locally and fails in production because the batch image drifted. The `wait-for-it.sh` gates mean the container is only ready once its dependencies are, so a job firing at midnight cannot hit a database that has not finished starting.

### Why not Airflow

Three jobs. One machine. No fan-out, no dynamic tasks, no branching, no backfills. Airflow means a scheduler, a webserver, a metadata database, and an executor — more infrastructure than the pipeline it would orchestrate, and more operational surface than the thing being operated.

**What that costs, precisely:**

- **No retries.** A job that fails is failed until the next scheduled run.
- **No backfill.** There is no "re-run last Tuesday" for a job whose command is not parameterised by date.
- **No dependency enforcement.** `transform` and `indicators` both fire at `@midnight`, and `transform` simply assumes the 6-hourly `ingest` has finished and that `indicators` has landed its data. Nothing checks. In practice `ingest` completes in minutes and both midnight jobs read tables the other does not write, so collisions do not occur — but that is a property of current timing, not a guarantee, and it will break silently the first time `ingest` runs long.
- **No run history.** Ofelia knows whether a command exited non-zero. Everything else about what a run did lives in `ops.ingestion_runs`, because the ingest job writes it there itself.

That last point is worth noticing: the ingest job's own run tracking ([Ingestion](02-ingestion.md)) is exactly the observability Airflow would have provided, implemented in the job rather than the orchestrator. That is why the lightweight scheduler is viable. `indicators` and `transform` have no equivalent, which is why they are the two jobs that would benefit most from a real orchestrator first.

### Alerting

Each job carries SMTP configuration:

```yaml
ofelia.job-exec.ingest.smtp-host: "${SMTP_HOST}"
ofelia.job-exec.ingest.email-to: "${ALERT_EMAIL_TO}"
ofelia.job-exec.ingest.mail-only-on-error: "true"
```

`mail-only-on-error: true` is the important flag. A daily "job succeeded" email is an email people stop reading within a fortnight, and the day it stops arriving nobody notices. Alerting only on failure keeps the signal meaningful.

The alert fires on **non-zero exit**. That determines what is actually alertable, and it is a real constraint:

- `make dbt-build` exits non-zero when a data test fails — so [data quality failures](06-data-quality.md) do produce an alert.
- The KSH parser's `ValueError` propagates and exits non-zero — so a structural change to the KSH page alerts.
- An `ingest` run where **every single item failed** still exits 0, because per-item failures are caught and recorded rather than raised, and `finish_run` marks the run `completed` unconditionally. That is the largest hole in the alerting, and it is [Limitations](08-limitations.md) item 5.

## Migrations

A hand-written runner, ~40 lines ([`core/migrate.py`](../api/packages/core/src/ingatlanmizu/core/migrate.py)):

```python
TRACKING = """
CREATE SCHEMA IF NOT EXISTS ops;
CREATE TABLE IF NOT EXISTS ops.schema_migrations (
    filename    text PRIMARY KEY,
    applied_at  timestamptz NOT NULL DEFAULT now()
);
"""

for path in sorted(MIGRATIONS.glob("*.sql")):
    if path.name in applied:
        continue
    try:
        conn.execute(path.read_text())
        conn.execute("INSERT INTO ops.schema_migrations (filename) VALUES (%s)", (path.name,))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise RuntimeError(f"Migration failed: {path.name}: {exc}") from exc
```

Filename as primary key, lexicographic ordering by the numeric prefix, one transaction per file, and a rollback-and-abort on the first failure so a broken migration never leaves the schema half-applied or lets subsequent migrations run against an unexpected state.

It is **idempotent**, which is what makes the deployment model work: the `migrate` service runs on every `docker compose up`, applies whatever is pending, and exits. No manual step, no "did someone remember to migrate?"

### Why not Alembic

Alembic's main value is autogenerating migrations by diffing an ORM's models against the live schema. There is no ORM here — every query in the codebase is hand-written SQL — so there is nothing to diff, and autogenerate has nothing to offer.

The schema also uses features that hand-written SQL expresses directly and autogenerate tends to mangle: schema creation, `DROP SCHEMA public`, PL/pgSQL trigger functions ([005](../api/db/migrations/005_add_timestamps.sql)), and a composite index with a descending sort key ([015](../api/db/migrations/015_add_ad_key_created_at_index_to_zenga_listings.sql)).

**What it costs:** no downgrades. There is no `down` half to any migration; reversing a change means writing a new forward migration. For an append-only warehouse where the recovery path is "restore and replay" that is an acceptable trade, and it would not be for an application database.

The migration sequence also has a **gap at `006`** — a file renamed during development (`1ed19c8 Rename migration`). Because tracking is by filename rather than by sequence number, the gap is inert: nothing scans for contiguity. Worth knowing before someone goes looking for a missing file.

23 migration files numbered `001`–`024` (with the `006` gap) are the most readable history of the schema's evolution; [Change detection](03-change-detection.md) reads part of it as a narrative.

## Configuration

Pydantic Settings, loaded once at import ([`core/config.py`](../api/packages/core/src/ingatlanmizu/core/config.py)):

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql://postgres:root@127.0.0.1:54320/ingatlanmizu"

    s3_endpoint_url: str      # no default — required
    s3_bucket: str            # no default — required
    s3_access_key: str        # no default — required
    s3_secret_key: str        # no default — required

    ingest_max_workers: int = 8

settings = Settings()
```

Two properties are doing the work.

**Typed and validated at import.** `ingest_max_workers` is an `int`, so `INGEST_MAX_WORKERS=eight` fails at startup with a clear pydantic error rather than at the `ThreadPoolExecutor` call twenty minutes into a run.

**Required fields have no defaults.** The four S3 settings are declared without defaults deliberately: a container started without S3 credentials fails **immediately at import**, not at the first `put_object` after a page has already been fetched. Failing at startup is a deployment problem; failing mid-run is a data problem.

The database settings *do* have defaults, pointing at a local development instance — convenient locally, and a small risk in that a misconfigured deployment falls back to a connection attempt rather than an error. In practice `docker-compose.yml` injects all of them via a YAML anchor (`x-common-variables`), so every service receives an identical environment and configuration cannot drift between the API, the scheduler, and the migrate job.

## Database connections

Two shapes, deliberately different ([`core/db.py`](../api/packages/core/src/ingatlanmizu/core/db.py)):

```python
@contextmanager
def connection() -> Generator[psycopg.Connection, None, None]:
    """One short-lived connection with an explicit transaction."""
    with psycopg.connect(
        str(settings.database_url),
        autocommit=False,
        options="-c statement_timeout=300000",
    ) as conn:
        yield conn


@lru_cache(maxsize=1)
def pool() -> ConnectionPool:
    return ConnectionPool(str(settings.database_url), min_size=1, max_size=10, open=True)
```

**Batch jobs** open a connection, do their work in an explicit transaction, and close. Connection setup cost is irrelevant next to a job that runs for minutes, and `autocommit=False` means multi-statement work is atomic by default rather than by remembering. The 300-second `statement_timeout` is a backstop: a runaway query in a nightly job dies rather than holding locks until someone notices.

**The API** uses a pool, because connection setup cost is very much not irrelevant when it happens per HTTP request. `lru_cache(maxsize=1)` makes it a lazily-created singleton — built on first use rather than at import, so importing the module in a context that never queries (a test, a CLI) does not open connections.

Using one abstraction for both is a common mistake in either direction: a pool in a short-lived batch process leaks connections at exit, and per-request connections in a web service add latency to every call. These are different problems and they get different tools.

## Packaging

A uv workspace ([`pyproject.toml`](../api/pyproject.toml)) with four packages:

```
packages/core         config, database, migrations       — depends on nothing internal
packages/ingest       zenga crawl                        — depends on core
packages/indicators   MNB / Bankmonitor / KSH            — depends on core
packages/api          FastAPI read layer                 — depends on core
```

The boundaries are declared as dependencies in each package's `pyproject.toml`, which makes them enforced rather than aspirational: `ingest` cannot import from `indicators`, because it does not depend on it and the import fails. `core` cannot import from either, so shared infrastructure stays free of domain knowledge. Architecture that is checked by the build survives; architecture that lives in a diagram does not.

Each package declares console scripts, wired to the Makefile:

```makefile
runingest:      uv run ingest
runindicators:  uv run ingest-indicators
runapi:         uv run api
migrate:        uv run migrate
```

The dbt targets prefix an environment loader, since dbt reads database credentials from `env_var()` in [`profiles.yml`](../api/transform/profiles.yml):

```makefile
DBT_ENV := set -a && . ./.env && set +a && export DBT_PROFILES_DIR=transform DBT_PROJECT_DIR=transform

dbt-build:
	@$(DBT_ENV) && uv run dbt build
```

## Deployment

```bash
make deploy
```

Runs [`deploy/deploy.sh`](../deploy/deploy.sh): `rsync` the working tree to the host (excluding `.venv`, `.env`, `.git`, data directories, and dbt artifacts), then `docker compose down` and `up -d --build` over SSH.

Caddy terminates TLS and provisions certificates automatically from `SITE_ADDRESS`; the API is not published to the host at all, only reachable through the proxy on the compose network.

**What this costs, plainly:** no CI, so nothing lints or tests on push. No build artifact, so what runs in production is whatever was in the working tree at deploy time — including uncommitted changes. No rollback beyond re-deploying an older checkout. And `docker compose down` before `up` means a brief outage on every deploy. All of these are fine for a single-author project and none of them would be fine with a second engineer.

## Inspecting a run

The queries worth knowing.

**Recent runs:**

```sql
select id, source, status, discovered_count, started_at, completed_at,
       completed_at - started_at as duration
from ops.ingestion_runs
order by id desc
limit 10;
```

**Item outcomes for one run:**

```sql
select status, count(*), count(*) filter (where new_record_created) as changed
from ops.ingestion_run_items
where ingestion_run_id = 42
group by status;
```

**Why items failed:**

```sql
select external_id, url, left(error_message, 300)
from ops.ingestion_run_items
where ingestion_run_id = 42 and status = 'failed';
```

**Which seeds a run used** — the audit trail described in [Ingestion](02-ingestion.md):

```sql
select jsonb_pretty(metadata) from ops.ingestion_runs where id = 42;
```

**Warehouse size:**

```sql
select
  (select count(*) from bronze.zenga_listing_versions)            as versions,
  (select count(*) from bronze.zenga_observations)                as observations,
  (select count(distinct listing_code) from bronze.zenga_observations) as distinct_listings,
  (select count(*) from ops.ingestion_runs)                       as runs,
  (select min(observed_at)::date from bronze.zenga_observations)  as first_observation;
```

**Stuck items** — the at-least-once edge case from [Change detection](03-change-detection.md), items that loaded but were never marked complete:

```sql
select ingestion_run_id, count(*)
from ops.ingestion_run_items
where status in ('extracting', 'extracted')
  and created_at < now() - interval '1 day'
group by ingestion_run_id;
```

## Local development

```bash
make up                    # full stack: postgres, minio, api, frontend, proxy, scheduler
```

Migrations apply automatically via the `migrate` service. Note that `.env.example` covers only 12 of the 29 variables `docker-compose.yml` interpolates — the ports, MinIO credentials, `SITE_ADDRESS`, schedules, and SMTP settings have to be added by hand ([Limitations](08-limitations.md)). To drive the pipeline by hand, from `api/`:

```bash
make migrate               # apply pending migrations
make runingest             # one full crawl: discover, extract, load
make runindicators         # MNB, Bankmonitor, KSH
make dbt-build             # rebuild silver and gold, running tests
make dbt-test              # tests only
make dbt-freshness         # source freshness only
make dbt-docs              # generate and serve the dbt documentation site
```

`make dbt-docs` is worth running once — it renders the full model DAG, every column description, and every test as a browsable site, which is the fastest way to get oriented in the transformation layer.

MinIO's console is on `MINIO_FRONTEND_PORT` (default mapping in `.env`), which is the quickest way to confirm raw HTML is landing where [Ingestion](02-ingestion.md) says it should.

---

[← Data quality](06-data-quality.md) · [Docs index](README.md) · [Next: Limitations →](08-limitations.md)
