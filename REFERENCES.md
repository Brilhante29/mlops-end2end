# References

## Primary Documentation

| Decision | Source | How it is used |
|---|---|---|
| Stable Dag authoring | [Apache Airflow Task SDK](https://airflow.apache.org/docs/task-sdk/stable/) | `airflow.sdk` decorators keep Dag code on the supported public surface. |
| Local Dag execution | [Airflow Dag testing](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#testing-dags) | `dag.test()` executes the complete dependency graph in the benchmark. |
| Container baseline | [Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/3.3.0/howto/docker-compose/index.html) | Official 3.3.0 Python image and exact-version extension rule. |
| Reproducible dependencies | [Airflow 3.3.0 Python 3.12 constraints](https://raw.githubusercontent.com/apache/airflow/constraints-3.3.0/constraints-3.12.txt) | Compatibility reference for overlapping runtime packages. |
| Registry deployment contract | [MLflow Model Registry workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/) | Database-backed registry, model tags, `champion` alias, and alias-based loading. |
| Data validation | [Pandera documentation](https://pandera.readthedocs.io/) | Strict schema before a frame reaches training. |
| Deterministic fixture | [scikit-learn `make_classification`](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_classification.html) | Locally generated binary dataset with explicit seed. |
| Typed inference | [FastAPI documentation](https://fastapi.tiangolo.com/) | REST, OpenAPI, validation, health, and prediction endpoints. |
| Metrics exposition | [Prometheus Python client](https://github.com/prometheus/client_python) | Prediction counter, latency histogram, and loaded-model gauge. |

## Organizational References

- [Paulescu/hands-on-train-and-deploy-ml](https://github.com/Paulescu/hands-on-train-and-deploy-ml): problem-first narrative, `src/tests`, automation, and a short end-to-end run path. No code or vendor stack was copied.
- [Paulescu/kubernetes-for-ml-engineers](https://github.com/Paulescu/kubernetes-for-ml-engineers): explicit local workflow and reproducible container steps. Kubernetes is deliberately out of scope here.
- `portfolio-reuse-kit`: component pack, decision brain, OpenSpec governance, language profiles, skills, SDD, design tokens, benchmark contract, and validator.

External repositories are references, not hidden runtime dependencies. Product code in this repository is original.

