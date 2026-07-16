# Intent: mlops-end2end

## Measurable Claim

A single local-first command validates data, trains and quality-gates a model, promotes an MLflow alias, serves it with FastAPI, exports Prometheus metrics, and measures elapsed time to production.

## Problem

Establishes the reusable model lifecycle used by later data quality, feature serving, drift detection, and applied-vision projects.

## In Scope

- Use the selected component pack: `mlops-data-platform`.
- Keep the project under the MLOps and Data Platform program.
- Preserve the benchmark contract: `time_to_production_seconds` in `benchmarks/results/summary.json`.
- Keep the default path local-first and reproducible.

## Out Of Scope

- Paid credentials for the default demo.
- External infrastructure that is not required by the benchmark.
- Replacing local portfolio skills with external components silently.

## Default Demo Path

- Status: benchmarked
- Runtime: Official Apache Airflow slim 3.3.0 Python 3.12 image pinned by OCI digest with a CPU-only local lifecycle
- Benchmark command: `docker run --rm mlops-end2end`

## Public Proof

- Benchmark: time_to_production_seconds = 371.94 seconds
- Result path: `benchmarks/results/summary.json`
