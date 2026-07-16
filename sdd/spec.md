# Spec: mlops-end2end

## Number and Claim

#21 proves that a deterministic model can move through validated training, tracked registration, quality-gated alias promotion, monitored serving, and numeric evidence from one local Docker command.

## Portfolio Program

`mlops-data-platform`. This is the lifecycle foundation for #22 drift, #23 feature serving, #26 data quality, and training repositories in applied computer vision.

## In Scope

- Synthetic binary classification fixture with seed `42`.
- Strict Pandera schema before training.
- Airflow 3 Dag with explicit dependencies and retries.
- scikit-learn CPU model with ROC AUC and accuracy.
- MLflow run, registered version, tags, and `champion` alias.
- Pure promotion policy behind a registry port.
- FastAPI prediction and health contracts.
- Prometheus request, latency, and loaded-model metrics.
- Lifecycle and serving benchmark JSON.

## Out of Scope

- Real domain claims or production data.
- Drift, feature store, streaming, retraining schedule, distributed executor, Kubernetes, cloud, high availability, authentication, or a frontend.

## User-Visible Contract

```bash
docker build -t mlops-end2end .
docker run --rm mlops-end2end
```

The command SHALL require no secret and SHALL print a JSON object with `time_to_production_seconds`, ROC AUC, accuracy, inference p95, throughput, run ID, model version, alias, environment, and command.

## Dataset

- Source: `sklearn.datasets.make_classification`.
- Size: 1,200 rows, 8 float features, one binary target.
- Split: 75% train and 25% test, stratified.
- Seed: 42.
- License/external dependency: generated locally; no downloaded dataset.

## Definition of Done

- [x] Architecture and technical choices answer the OpenSpec self-challenge.
- [x] Core policy is framework-independent and unit tested.
- [x] Data contract, Dag, tracking, registry, API, and telemetry are implemented.
- [ ] Rebuilt Docker image passes from a clean clone with the resolved base digest.
- [ ] Unit coverage is at least 80% for measured core modules in the rebuilt image.
- [ ] Three rebuilt-image benchmark runs complete with no failed lifecycle stage.
- [ ] README opens with the rebuilt-image confirmed median number.
- [x] Reuse improvements are patched, backlogged, or rejected.
- [ ] Public CI is green.

