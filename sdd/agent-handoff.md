# Agent Handoff: mlops-end2end

## Mission

Ship #21 as the first executable foundation of the MLOps and Data Platform program. Preserve the one-command, no-secret, CPU-only path and publish only after three benchmark runs and green CI.

## Source Order

1. `openspec/changes/ship-mlops-end2end/` for approved scope and self-challenge.
2. `project.yaml` for portfolio contract and decision fields.
3. `sdd/` for architecture, stack, benchmark, and release evidence.
4. `.portfolio/` and local skills for reusable standards.
5. Product code and tests for implementation truth.

## Invariants

- Domain and application policy import no Airflow, MLflow, FastAPI, storage, broker, cloud SDK, or UI code.
- Promotion occurs only through the quality gate and a registry port.
- Serving resolves the `champion` alias, never a hard-coded version.
- Default execution downloads no data and uses no credential.
- Airflow uses the public `airflow.sdk` authoring surface.
- No broker, cloud, drift engine, feature store, microservice split, or UI is added without an OpenSpec change and benchmark force.
- Docker remains the system-agnostic entrypoint.

## Current Verification Order

1. Lint `src`, `tests`, and `dags`.
2. Run unit tests with at least 80% measured-core coverage.
3. Run the full Docker lifecycle and inspect JSON proof.
4. Retain three successful runs with the same image content; report median, range, and failures.
5. Complete reuse review and patch the kit.
6. Publish, then inspect GitHub Actions logs and artifact.

## Failure Triage

- Dependency conflict: preserve Airflow 3.3.0 and its official image contract before changing an app dependency.
- Dag failure: read `pipeline.log`; do not bypass orchestration in the benchmark.
- Registry failure: confirm the direct SQLite tracking URI, local artifact path, and registered version before alias assignment.
- Service failure: confirm alias resolution and pyfunc `predict_proba` output before loosening health checks.
- Slow result: report environment and stage evidence before optimizing or removing required lifecycle work.

## Current Evidence\n\n- Source commit: 9e8c76d02a2a7f10c8ccee7049cd21fc47b9db12.\n- Image: sha256:5228391a3b888a26c0fa5263d5a2393694ee6f862a80e48d7839ad22a2fb541f.\n- Lifecycle samples: 57.373 s, 59.140 s, 58.696 s; median 58.696 s; zero failures.\n- Airflow execution: dags-test; MLflow tracking: sqlite-direct; alias: champion.\n- V2:
epeat=3, measured_iterations=3, raw artifact digest sha256:f980b4a86c54fbcb66db888ee22a4d633c32726f7118cef2c609572a23246a81.\n- Remaining gate: commit/push evidence and inspect exact-head CI.\n
