# End-to-End MLOps: From Validated Data to a Governed, Served Model in One Command

> **58.696 seconds median time to production:** an Airflow DAG validates data, trains, registers in MLflow, passes a quality gate, promotes the `champion` alias, and FastAPI serves it with ROC AUC `0.928`, inference p95 `72.733 ms`, and `160.275 req/s`, with zero failures across three clean runs.

[![validate](https://github.com/Brilhante29/mlops-end2end/actions/workflows/validate.yml/badge.svg)](https://github.com/Brilhante29/mlops-end2end/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![Airflow 3](https://img.shields.io/badge/Airflow-3-017CEE?logo=apacheairflow&logoColor=white) ![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white)

## Why this exists

Most machine-learning projects stop at a notebook with a good metric. The part that decides whether a model can be trusted in production is everything after it: who validated the input data, which run produced the deployed model, what quality bar it had to clear, how the service knows which version to load, and how anyone measures the whole path. This repository makes that path executable and timed:

- input data is checked against a Pandera contract before training;
- an Airflow 3 DAG runs the stages with real task dependencies and retries (`airflow dags test`);
- MLflow records the run and model version, and a pure-domain ROC AUC gate decides promotion;
- FastAPI resolves the mutable `champion` alias instead of a hard-coded version, and exposes Prometheus metrics;
- the primary timer stops only when the alias-backed health check succeeds.

## Results

Three clean lifecycle runs, each in a fresh container:

| Metric | Median | Samples |
|---|---:|---:|
| Time to production | **58.696 s** | 57.373 / 59.140 / 58.696 s |
| ROC AUC | **0.928** | identical quality across 3 runs |
| Inference p95 | **72.733 ms** | 300 requests/run after 20 warm-ups |
| Throughput | **160.275 req/s** | concurrency 8 |
| Image size | **1,532,464,403 bytes** | immutable source image |

The time-to-production range is `1.767 s`, or `3.0104%` of the median.

| Lifecycle stage | Median |
|---|---:|
| Airflow metadata migration | 9.684 s |
| Airflow DagRun, training, registry, and promotion | 38.355 s |
| Alias-backed API startup | 10.581 s |

## Quickstart

```bash
docker build -t mlops-end2end .
docker run --rm mlops-end2end
```

No API key, cloud account, GPU, host Python, or manual promotion is required. The command prints the complete JSON result; to keep it:

```bash
docker run --rm -v "$(pwd)/benchmarks/results:/results" -e BENCHMARK_OUTPUT=/results/local.json mlops-end2end
```

Publication evidence (three clean lifecycle containers, raw V1 plus provenance-rich V2): `python tools/publish_benchmark.py`.

## How it works

```mermaid
flowchart LR
  A["Deterministic fixture"] --> B["Pandera contract"]
  B --> C["Airflow Task SDK DAG"]
  C --> D["scikit-learn training"]
  D --> E["MLflow run and model version"]
  E --> F["Pure ROC AUC gate"]
  F --> G["champion alias"]
  G --> H["FastAPI inference"]
  H --> I["Prometheus metrics"]
  I --> J["Benchmark JSON"]
```

The style is a pipeline, because the problem is an ordered, retryable artifact lifecycle. Ports and adapters appear only where they earn their cost: the promotion policy in `domain/` and `application/` depends on a small registry port, not on MLflow, so tests swap in a recording registry. Airflow, MLflow, FastAPI, storage, and Prometheus stay outside that policy.

## Design decisions

| Decision | Why | Rejected |
|---|---|---|
| Airflow 3 (`airflow.sdk`), slim image pinned by digest | Dependencies, retries, and stage evidence are part of the claim | Cron plus scripts |
| MLflow registry over SQLite, alias-based serving | Governance without a redundant tracking server; deploys follow the alias | Hard-coded model versions |
| Quality gate as pure domain code | Promotion rules are testable without infrastructure | Gate logic inside the DAG |
| REST for inference | One fixed command-shaped operation | GraphQL (no selection or aggregation need) |
| No broker, no cloud | No event stream or AWS behavior in the measured path | Kafka or cloud services as decoration |

Full trade-offs and self-questions: [OpenSpec design](openspec/changes/ship-mlops-end2end/design.md) and [architecture decision](sdd/architecture-decision.md).

## Testing

```bash
docker run --rm --entrypoint ruff mlops-end2end check src tests dags
docker run --rm --entrypoint pytest mlops-end2end -q
```

Unit tests cover data contracts, the quality gate, configuration, and the API, with an 80% coverage gate on domain, application, and data adapters. The default Docker run is the integration, contract, and benchmark proof.

## Limitations

- Synthetic, deterministic classification data; this is not a medical, financial, or risk model.
- SQLite and single-process services are local benchmark choices, not a high-availability design.
- Drift detection is intentionally separate; see [model-drift-detector](https://github.com/Brilhante29/model-drift-detector).

## Reproducibility

- Source commit `9e8c76d`; image digest `sha256:5228391a3b888a26c0fa5263d5a2393694ee6f862a80e48d7839ad22a2fb541f`.
- Evidence HEAD `0249659` passed every gate in [GitHub Actions run 30780951251](https://github.com/Brilhante29/mlops-end2end/actions/runs/30780951251).
- In V2 evidence, `measured_iterations=3` counts lifecycle samples; `warmup_iterations=20` and concurrency 8 apply to the secondary HTTP measurement.

## Project structure

```text
dags/                        Airflow DAG
src/mlops_end2end/domain/    ROC AUC quality policy
src/mlops_end2end/application/   registry port and promotion use case
src/mlops_end2end/adapters/  data contract, training, MLflow registry
src/mlops_end2end/           API, pipeline runner, configuration
tests/                       unit tests with a recording registry
benchmarks/  tools/          results, publication producer, validators
sdd/  openspec/              specification, architecture and technical decisions
```

## How this repository is built

The project follows the spec-driven workflow of [portfolio-reuse-kit](https://github.com/Brilhante29/portfolio-reuse-kit). Requirements and decisions live in [`sdd/`](sdd) and [`openspec/`](openspec), and [`project.yaml`](project.yaml) records the architecture, stack, and rejected alternatives. Development is AI-assisted and human-governed: [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md) hold the coding-agent instructions, while tests, validators, and CI decide what gets published.

## Related work

- [model-drift-detector](https://github.com/Brilhante29/model-drift-detector): post-deployment monitoring.
- [feature-store-lite](https://github.com/Brilhante29/feature-store-lite) and [data-quality-checks](https://github.com/Brilhante29/data-quality-checks): the data side of the lifecycle.
- [vision-serving-fastapi](https://github.com/Brilhante29/vision-serving-fastapi): serving a computer-vision checkpoint.

See [`REFERENCES.md`](REFERENCES.md) for documentation and attribution.

## Author

**Guilherme Brilhante**, software engineer working on scalable backends and production AI.
[LinkedIn](https://www.linkedin.com/in/guilhermefreirebrilhanteseveriano/) · [GitHub](https://github.com/Brilhante29) · [Publications](https://dblp.org/pid/353/6812.html)

## License

[MIT](LICENSE).
