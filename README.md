# #21 mlops-end2end

> **371.941 seconds current time to production:** one successful local lifecycle run, ROC AUC `0.928441`, inference p95 `285.557 ms`, and no paid service or credential.

This repository proves the complete operational path around a small CPU model: orchestration, data validation, experiment tracking, registry governance, quality-gated promotion, inference, telemetry, and reproducible evidence.

## Run

```bash
docker build -t mlops-end2end .
docker run --rm mlops-end2end
```

No API key, cloud account, GPU, host Python, shell-specific script, or manual promotion is required. The same commands work on Linux, macOS, and Windows with Docker.

## Benchmark

The current baseline starts inside the container before local metadata stores are initialized. The image keeps the Airflow Dag as its orchestration contract and executes the same stages directly because a one-shot `docker run` does not start a scheduler. It stops only when FastAPI is healthy with `models:/portfolio-risk-model@champion` loaded.

| Metric | Baseline | What it proves |
|---|---:|---|
| Time to production | **371.941 s** | Full lifecycle friction from empty runtime to healthy promoted model |
| ROC AUC | **0.928441** | Candidate quality before promotion |
| Inference p95 | **285.557 ms** | Serving latency after promotion |
| Throughput | **37.975 req/s** | CPU request capacity for the fixed fixture |
| Image size | not captured in this run | Supplementary image footprint, not part of the primary gate |

This committed JSON is the first current runtime baseline after the Airflow 3.3 execution fix. A three-run median remains the publication gate; this result is not presented as a cross-machine performance promise.

| Lifecycle stage | Current run |
|---|---:|
| MLflow startup | 93.637 s |
| Airflow metadata migration | 37.410 s |
| Airflow stages, training, registry, and promotion | 165.203 s |
| Alias-backed API startup | 75.691 s |

The command prints the complete JSON result. A bind mount can persist it:

```bash
docker run --rm \
  -v "$(pwd)/benchmarks/results:/results" \
  -e BENCHMARK_OUTPUT=/results/local.json \
  mlops-end2end
```

PowerShell uses the same image with `${PWD}` in the volume value.

## System

```mermaid
flowchart LR
  A["Deterministic fixture"] --> B["Pandera contract"]
  B --> C["Airflow Task SDK Dag"]
  C --> D["scikit-learn training"]
  D --> E["MLflow run and model version"]
  E --> F["Pure ROC AUC gate"]
  F --> G["champion alias"]
  G --> H["FastAPI inference"]
  H --> I["Prometheus metrics"]
  I --> J["Benchmark JSON"]
```

Pipeline architecture is the primary style because the problem is an ordered, retryable artifact lifecycle. A ports-and-adapters boundary is used only where it earns its cost: the domain quality policy depends on a small registry port, not MLflow. Airflow, MLflow, FastAPI, storage, and Prometheus remain outside that policy.

## Decisions

- **Airflow:** dependencies, retries, and stage evidence are part of the claim; the Dag uses the stable Airflow 3 `airflow.sdk` surface and the official slim image pinned by OCI digest.
- **MLflow:** a database-backed local registry records runs and versions; FastAPI resolves the mutable `champion` alias instead of a hard-coded version.
- **REST:** prediction is one fixed command-shaped operation. GraphQL adds no selection or aggregation value here.
- **No broker:** there is no event stream, fan-out, or asynchronous throughput requirement, so Kafka and RabbitMQ would be decorative.
- **No cloud:** the measured path exercises no AWS behavior. Kumo becomes the first local option only when a concrete AWS service enters scope.
- **No drift:** this service exports the evidence that #22 will consume; drift detection keeps its own repository and benchmark.

The complete tradeoffs and self-questions live in [OpenSpec](openspec/changes/ship-mlops-end2end/design.md) and [SDD](sdd/architecture-decision.md).

## Verification

```bash
docker run --rm --entrypoint ruff mlops-end2end check src tests dags
docker run --rm --entrypoint pytest mlops-end2end -q
docker run --rm --entrypoint pytest mlops-end2end tests/test_quality.py tests/test_data.py tests/test_runner.py --cov=mlops_end2end.domain --cov=mlops_end2end.application --cov=mlops_end2end.adapters.data --cov-report=term-missing --cov-fail-under=80
```

Unit tests substitute the MLflow adapter with a recording registry, proving DIP and LSP at the promotion boundary. The default Docker run is the integration, contract, and benchmark proof.

## Scope

The generated classification data is synthetic, deterministic, CPU-only, and not a medical, financial, or production risk model. SQLite and single-process services are deliberate local benchmark choices, not a high-availability deployment recommendation.

## Reuse

The repository consumes the decision brain, component pack, OpenSpec schema, architecture selector, language profiles, skills, SDD templates, design tokens, validator, and benchmark contract from `portfolio-reuse-kit`. Project-specific training and serving code remains here.

See [REFERENCES.md](REFERENCES.md) for primary documentation and attributed organizational references.
