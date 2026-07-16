# Change: Ship the train-to-production MLOps proof

## Why

The MLOps and Data Platform program needs one executable reference that proves a model can move from validated data to a monitored inference endpoint without paid credentials or manual promotion.

## Portfolio Impact

- Establishes the lifecycle contract reused by model-drift-detector, feature-store-lite, data-quality-checks, and the computer-vision training repositories.
- Demonstrates Python, Airflow, MLflow, FastAPI, Prometheus, Docker, data contracts, model governance, and reproducible benchmarking in one bounded system.
- Produces a post-ready number: elapsed seconds from an empty runtime to a healthy endpoint backed by the promoted model alias.

## Capabilities

- `orchestrated-training`: deterministic generate, validate, train, register, gate, and promote stages.
- `alias-backed-serving`: inference loads the registry alias instead of a hard-coded model version.
- `lifecycle-benchmark`: measures time to production, model quality, and serving latency.
- `observable-inference`: exports request and model metadata through Prometheus.

## Non-Goals

- Drift detection, online feature serving, streaming ingestion, distributed executors, cloud deployment, and production high availability.

