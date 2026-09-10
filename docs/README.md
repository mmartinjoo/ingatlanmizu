# Documentation

Technical documentation for the `ingatlanmizu` data pipeline: a longitudinal record of the Hungarian property market, assembled from four sources and served as monthly market statistics.

These documents cover **ingestion through the gold marts** — the data engineering. The API and frontend are described only where they explain a decision upstream of them.

## If you have five minutes

Read [Ingestion](02-ingestion.md). It is the centrepiece, and the two sections worth reading even if you read nothing else are:

- **[Stages are driven by database state, not process memory](02-ingestion.md#stages-are-driven-by-database-state-not-process-memory)** — why a run's stages communicate through Postgres rather than through function arguments, and what that buys.
- **[Raw-first storage](02-ingestion.md#raw-first-storage)** — why every page is written to object storage before anything is allowed to parse it.

Then skim [Change detection](03-change-detection.md) for the versioning scheme, and [Limitations](08-limitations.md) for an honest account of what is wrong with all of it.

## Contents

| | Document | What it covers |
|---|---|---|
| 01 | [Architecture](01-architecture.md) | System overview, the four sources, the medallion layering in Postgres, container topology, and the reasoning behind each technology choice |
| 02 | [Ingestion](02-ingestion.md) | The listings crawler. Three stages driven by database state, a status machine used as a work queue, per-item failure isolation, thread-local HTTP sessions, raw-first object storage, the `Source` abstraction, and the parsing strategy |
| 03 | [Change detection](03-change-detection.md) | Append-only versioning, SHA-256 payload hashing and what it deliberately excludes, why presence and content live in separate tables, and the delivery semantics that follow |
| 04 | [Market indicators](04-indicators.md) | MNB, Bankmonitor, and KSH — three acquisition shapes and three different idempotency strategies, chosen from each source's publication behaviour |
| 05 | [Transformations](05-transformations.md) | The dbt layer. Cleaning macros as a domain vocabulary, the multi-source union seam, and the point-in-time monthly join that keeps historical months from silently rewriting themselves |
| 06 | [Data quality](06-data-quality.md) | Four layers of defence: boundary filters, grain assertions, value bounds with a deliberate error/warn split, and source freshness — plus the fail-loud philosophy behind them |
| 07 | [Operations](07-operations.md) | Label-driven scheduling, alerting, the hand-rolled migration runner, configuration, connection strategy, deployment, and the queries for inspecting a run |
| 08 | [Limitations](08-limitations.md) | Twelve specific known defects and constraints, two of them active bugs, each with the fix — and a prioritised roadmap |

## Reading order

The documents are written to be read in sequence, following the data: a page on zenga.hu enters at [Ingestion](02-ingestion.md), is versioned in [Change detection](03-change-detection.md), is cleaned and aggregated in [Transformations](05-transformations.md), and is validated in [Data quality](06-data-quality.md).

They are also written to be read individually. Each is self-contained and links to the others where a decision made in one explains a constraint in another.

## A note on language

The source data is Hungarian, and so are the identifiers in the `bronze` layer: `hirdeteskod` (listing code), `alapterulet` (floor area), `megye` (county), `ar` (price), `frissitve` (last updated). These are used as they appear in the code rather than translated away, and glossed on first use in each document. Everything from the silver layer upward is in English — the rename happens at the staging boundary, by design ([Transformations](05-transformations.md#staging-the-cleaning-layer)).

---

[← Back to the project README](../README.md)
