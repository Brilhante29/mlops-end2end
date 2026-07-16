# #21 mlops-end2end: time_to_production_seconds = 371.94 seconds

A single local-first command validates data, trains and quality-gates a model, promotes an MLflow alias, serves it with FastAPI, exports Prometheus metrics, and measures elapsed time to production.

This repository belongs to the MLOps and Data Platform program. Its job is narrow: prove the measurable claim through the selected component pack before adding unrelated infrastructure or features.

The benchmark is the proof. time_to_production_seconds = 371.94 seconds.  The result is stored in `benchmarks/results/summary.json` and can be reproduced from the Docker/local path.

The important architecture decision is pipeline. The problem is an ordered artifact lifecycle with retryable stages; pipeline architecture makes data, candidate, promotion, service, and evidence transitions explicit.

The default path stays local-first. The project uses python-ml, exposes rest-http, uses messaging mode `none`, and stores data with `SQLite for ephemeral Airflow and MLflow metadata`. The dependency rule is explicit: Airflow and MLflow adapters depend inward on application ports and domain policy; stages exchange artifact paths and identifiers instead of framework objects or large XCom payloads.

The rejected work matters as much as the implemented work. Anything that does not improve the benchmark stays out of the first version.

Post angle: start with the number, show the architecture boundary, then explain which future adapter can be added without changing the core use cases.
