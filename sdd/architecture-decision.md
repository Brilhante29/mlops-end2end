# Architecture Decision: Pipeline with Focused Ports

## Status

Accepted; benchmark reconfirmation is required after the harness evidence update.

## Context

The system must make an ML artifact lifecycle reproducible and inspectable. Integration pressure, data reproducibility, and auditability are high; domain complexity is medium; asynchronous throughput and independent deployment pressure are low.

## Decision

Use **pipeline architecture** for the system and a focused ports-and-adapters boundary around model promotion.

```text
dags/                    Airflow orchestration and retry policy
src/mlops_end2end/
  domain/                candidate metrics and quality policy
  application/           promotion use case and registry port
  adapters/              data contract, trainer, MLflow registry
  pipeline.py            stage composition
  api.py                 inference and telemetry adapter
  runner.py              local composition and benchmark harness
tests/                   isolated policy and contract tests
benchmarks/results/      reproducible evidence
```

Dependencies point inward. Domain and application modules import no Airflow, MLflow, FastAPI, database, broker, cloud SDK, or Prometheus code. The Dag exchanges small artifact paths and identifiers rather than serializing frames or models through XCom.

## Why It Fits

- Ordered artifacts and quality gates are the dominant force.
- Airflow owns scheduling semantics, dependencies, and retries without owning business policy.
- The registry port allows the policy to be tested and MLflow to be replaced without rewriting the gate.
- One image keeps the primary metric attributable to lifecycle work rather than network topology.

## Rejected Alternatives

| Alternative | Why rejected |
|---|---|
| MVC/layered | Controller-service-repository layers obscure stage artifacts and orchestration semantics. |
| Hexagonal as the primary label | Useful at the registry boundary, but external actor substitution is not the dominant system shape. |
| Microservices | No independent scale or deployment requirement; extra services inflate startup and failure modes. |
| Event-driven | No event stream or asynchronous throughput target exists. |
| Notebook-first | Weak operational reproducibility and unsuitable as the default Docker runtime. |

## Testing Strategy

- Unit: quality decisions and promotion behavior through a recording registry.
- Contract: deterministic fixture and Pandera rejection path.
- Adapter: model response mapping and metrics.
- Integration: one Docker run executes Airflow, MLflow, FastAPI, and Prometheus.
- Benchmark: elapsed lifecycle, quality, and serving metrics in one JSON record.

## Consequences

The image is larger because Airflow and MLflow coexist, and SQLite limits concurrent production use. These costs are explicit and acceptable for a portable lifecycle proof. A production migration can separate metadata services and executors while preserving stage and registry contracts.
