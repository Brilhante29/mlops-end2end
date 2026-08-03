# Benchmark Plan: Time to Production

## Hypothesis

A local CPU model can move from an empty metadata runtime to a healthy endpoint backed by an approved MLflow alias in a reproducible Docker run, while preserving visible quality and serving metrics.

## Primary Metric

`time_to_production_seconds_median`: median of three successful monotonic lifecycle measurements. Each run starts before local runtime initialization and stops only after MLflow registry initialization, Airflow metadata migration, Dag completion, quality-gated promotion, FastAPI startup, alias resolution, and a successful health response.

## Secondary Metrics

| Metric | Unit | Source | Why it matters |
|---|---:|---|---|
| `roc_auc` | ratio | held-out test set | Prevents a fast but invalid promotion. |
| `accuracy` | ratio | held-out test set | Readable secondary quality signal. |
| `inference_p50_ms` | milliseconds | 300 HTTP requests after 20 warmups | Typical serving latency. |
| `inference_p95_ms` | milliseconds | same request sample | Tail serving latency. |
| `inference_requests_per_second` | requests/second | 8-worker request window | CPU serving capacity for the fixed fixture. |

## Fixed Inputs

- 1,200 synthetic rows, 8 features, binary target.
- Seed 42 and stratified 75/25 train/test split.
- Logistic regression with scaling and maximum 500 iterations.
- ROC AUC promotion threshold 0.80.
- 20 inference warmups, 300 measured requests, concurrency 8.
- CPU only; no network download or external credential.

## Commands

```bash
docker build -t mlops-end2end .
docker run --rm mlops-end2end
```

To persist evidence, set `BENCHMARK_OUTPUT` to a mounted path. The JSON includes project, primary metric, value, unit, timestamp, command, environment, all secondary metrics, and registry/telemetry proof.

## Reproducibility Rules

- Record base image tag and digest, host Docker version, CPU allocation, architecture, package versions, fixture size, requests, concurrency, and seed.
- Retain at least three successful runs with the same image content; publish median, min, max, range relative to median, and every raw JSON result.
- Do not average away failures. Any failed stage invalidates the run and must be preserved with its reason.
- Do not compare time-to-production across machines without publishing environment differences.

## Current Baseline

- Three successful same-image lifecycle runs: 57.373 s, 59.140 s, and 58.696 s.
- Published median: 58.696 s; min 57.373 s; max 59.140 s; range 1.767 s (3.0104%).
- Median stages: Airflow migration 9.684 s, Airflow DagRun 38.355 s, API startup 10.581 s.
- Median quality: ROC AUC 0.928 and accuracy 0.87.
- Median serving: p50 48.604 ms, p95 72.733 ms, and 160.275 requests/second.
- Image size: 1,532,464,403 bytes; image digest `sha256:5228391a3b888a26c0fa5263d5a2393694ee6f862a80e48d7839ad22a2fb541f`.
- Raw runs, consolidated V1, and provenance-rich V2 are committed under `benchmarks/`.

## Post Angle

`#21 mlops-end2end: 58.696 seconds median from an empty local runtime to a quality-gated, alias-backed, monitored model API; Airflow DagRun, MLflow registry, AUC 0.928, and p95 72.733 ms included.`
