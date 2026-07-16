# Architecture Record: mlops-end2end

## Decision

- Architecture: `pipeline`
- Stack profile: `python-ml`
- API style: `rest-http`
- Messaging: `none`
- Database/runtime: `SQLite for ephemeral Airflow and MLflow metadata` / `Official Apache Airflow slim 3.3.0 Python 3.12 image pinned by OCI digest with a CPU-only local lifecycle`

## Reason

The problem is an ordered artifact lifecycle with retryable stages; pipeline architecture makes data, candidate, promotion, service, and evidence transitions explicit.

## Dependency Direction

Airflow and MLflow adapters depend inward on application ports and domain policy; stages exchange artifact paths and identifiers instead of framework objects or large XCom payloads.

## Boundaries

- deterministic data generation and Pandera contract
- framework-independent model quality and promotion policy
- scikit-learn training and MLflow tracking adapter
- MLflow registry alias adapter
- Airflow orchestration Dag
- FastAPI inference and Prometheus telemetry
- lifecycle benchmark and JSON evidence

## Library Policy

Use the stable Airflow Task SDK, MLflow database-backed registry aliases, Pandera at the data boundary, scikit-learn for deterministic CPU training, FastAPI/Pydantic for inference contracts, and Prometheus for framework-neutral metrics.

## Principle Check

- SRP: keep benchmark, API, use cases, and adapters separate.
- OCP: new providers must be adapters, not domain rewrites.
- LSP: replacement providers must preserve observable behavior.
- ISP: ports stay narrow.
- DIP: application depends on behavior, not infrastructure.
- KISS/YAGNI: leave out anything that does not improve the benchmark.
