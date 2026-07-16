# Benchmark Plan: Time to Production

## Hypothesis

A local CPU model can move from an empty metadata runtime to a healthy endpoint backed by an approved MLflow alias in a reproducible Docker run, while preserving visible quality and serving metrics.

## Primary Metric

`time_to_production_seconds_median`: median of three successful monotonic lifecycle measurements. Each run starts before local runtime initialization and stops only after MLflow readiness, Airflow metadata migration, Dag completion, quality-gated promotion, FastAPI startup, alias resolution, and a successful health response.

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

## Measured Result

- Three successful runs: 96.530 s, 118.832 s, and 123.678 s.
- Public result: 118.832 s median; 113.013 s mean; 22.845% max-min range relative to median.
- Median stages: MLflow 22.870 s, Airflow migration 14.621 s, pipeline 62.431 s, API 18.856 s.
- Quality was identical across all runs: ROC AUC 0.928441 and accuracy 0.87.
- Serving medians: p50 66.852 ms, p95 100.275 ms, and 115.415 requests/second.
- Validated image: `sha256:e12a38165f83bfbc775fec66f86f606c3825c027a927bd383c6120105672bff5`, 1,532,159,242 bytes.
- Raw evidence and the consolidated result are committed under `benchmarks/results/`.
## Post Angle

`#21 mlops-end2end: 118.832 seconds median from an empty local runtime to a quality-gated, alias-backed, monitored model API; AUC 0.928441 and p95 100.275 ms included.`
