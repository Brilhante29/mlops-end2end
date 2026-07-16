# Reuse Improvement Review

Project: `21 - mlops-end2end`

## Review Points

- [x] After scaffold: selected `mlops-data-platform`; rejected generic app architecture.
- [x] After architecture: pipeline became primary; ports retained only around material adapters.
- [x] After first slice: stable Airflow SDK and MLflow alias rules recorded.
- [x] After benchmark: dependency coexistence, metric fields, variance, image size, and failure diagnostics were reviewed.
- [x] Before publication review: proven reusable rules were staged in the kit and synchronized into this working copy; publication remains gated by the rebuilt benchmark.
- [x] After validation failure: CRLF/LF handling and tool availability became portable validation rules.

## Findings

| Finding | Classification | Kit area | Action | Status |
|---|---|---|---|---|
| The Python profile lacked a reusable lifecycle boundary for Airflow and MLflow. | `patch_now` | language profiles / skills | Added artifact-path stages, stable `airflow.sdk`, registry alias, pure quality gate, and focused coverage guidance. | patched and validated |
| OpenSpec needed an automatic self-challenge rather than an optional prose reminder. | `patch_now` | OpenSpec / SDD / generator | Added decision questions, answered architecture tradeoffs, revisit triggers, and reproducibility questions to generated artifacts. | patched and validated |
| Shared benchmark output needed lifecycle proof fields beyond one primary metric. | `patch_now` | contracts / harness | Extended generic result schemas for environment, metrics, proof, runs, and failures without coupling them to MLflow. | patched and validated |
| Airflow and MLflow dependency overlap can silently mutate the orchestrator. | `patch_now` | validation / skills | Require exact Airflow package retention and an OCI digest when extending an official Airflow image. | patched and validated |
| Readiness probes and JSON result parsing were conflated in the first implementation. | `patch_now` | benchmark harness skill | Separate liveness/readiness success from payload parsing in reusable benchmark guidance. | patched and validated |
| A regular Airflow image made the proof unnecessarily large. | `patch_now` | Python ML lifecycle skill | Prefer the official slim image when provider packages are not used; record the measured image delta. | patched and validated |
| Skill frontmatter validation assumed one newline convention. | `patch_now` | kit validator | Accept LF and CRLF explicitly so Linux, macOS, and Windows validate the same files. | patched and validated |
| The generic validator selected `unittest` and the host Python even when the project runtime was Docker and pytest. | `patch_now` | project validator | Compile structure on the host, defer runtime tests to the explicit container workflow, and use pytest only for non-Docker pytest projects. | patched and validated |
| The validator accepted historical benchmark JSON after source changes. | `patch_now` | project contract / validator | Added `benchmark.evidence_status`; changes mark evidence `invalidated`, and only a rebuilt, rerun, README-matched result can restore `current`. | patched and validated |
| Training, registry, and API code should move into the kit now. | `reject` | templates | Product code stays here; code extraction requires a second lifecycle project to demonstrate stable duplication. | rejected |
| A generic cloud adapter should be added to every MLOps repository. | `reject` | cloud matrix | Kumo is required only for concrete AWS behavior; cloud is absent from this measured path. | rejected |

## Final Gate

- [x] Reusable improvements were patched or recorded.
- [x] Project-specific implementation was not moved into the kit.
- [x] Validation reflects Airflow version safety, OCI digest pinning, lifecycle evidence freshness, and cross-platform text handling.
