# talent-pulse-lakehouse

Plug-and-play lakehouse turning raw job postings into live market trends. Medallion (Bronze/Silver/Gold) on Spark + Delta Lake + dbt — domain-agnostic: a new job domain is a config file, not new code.

## What it does

`de-job-intelligence` collects job postings around the clock. This repo turns that raw feed into a live dashboard of trending technologies: which skills are rising, which are fading, what pays, and what shows up together — repost-adjusted, with evidence behind every number.

## Plug-and-play by design

The domain is config, not code. Each domain is one file — `config/domains/<domain>.yaml` — holding the job-category filter, the skill taxonomy, and the dashboard label. The pipeline takes a `--domain` flag; Silver maps skills through that domain's taxonomy and Gold marts are keyed by domain. Adding DevOps or data science later means a new config file plus a taxonomy, not a new pipeline.

## Architecture

Oracle VM Postgres (OLTP) → incremental JDBC pull by watermark over Tailscale → de-lab Spark 4.2.1 + Delta Lake 4.4.1 on MinIO → Gold marts synced back to Postgres → dashboard on jobs.sriomkar.com.

- **Bronze** — raw postings, stamped with `description_coverage` (full/partial/none).
- **Silver** — dedup, entity resolution, skill bridge, quarantine.
- **Gold** — dbt marts: skill velocity, co-occurrence, compensation, recruiter funnel.

Trigger: the ingestion-finish webhook fires a batch run, with a nightly cron as backstop. Per-job triggering is deliberately rejected — Spark startup cost makes it wasteful.

## Stack

Apache Spark 4.2.1, Delta Lake 4.4.1, dbt Core, MinIO (S3), PostgreSQL 16, Python 3.12.

## Data quality

Not every row arrives complete: ~19% of collected postings have no usable job description (verified 2026-11-18), concentrated in the LinkedIn email-alert path. Bronze stamps coverage on every row; Silver extracts skills description-first and falls back to ingestion metadata at a lower confidence tier, recording `skill_source` on the bridge; rows that fail validation land in `silver.quarantine_jobs` with the failed rule — never in Gold, never dropped silently.

## Development

- Trunk-based: `main` is protected; every change arrives via a short-lived branch (`feat/`, `fix/`, `chore/`, `docs/`) and a pull request.
- Conventional commits: `<type>(<scope>): <summary>`.
- CI runs ruff, pytest, and dbt checks on every PR. Secrets live only in `.env` — never in code.
- Decisions are recorded as ADRs in `docs/adr/`.

## Status

Work proceeds in phases — trigger, Bronze, Silver, Gold, serving — one phase at a time, each merged through a PR.
