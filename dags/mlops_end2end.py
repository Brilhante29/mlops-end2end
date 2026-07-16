from __future__ import annotations

import pendulum
from airflow.sdk import dag, task

from mlops_end2end.pipeline import generate_stage, promote_stage, train_stage


@dag(
    dag_id="mlops_end2end",
    description="Generate, validate, train, register, and promote a deterministic model.",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["portfolio", "mlops", "local-first"],
)
def build_pipeline():
    @task(retries=1)
    def generate_and_validate() -> str:
        return str(generate_stage())

    @task(retries=1)
    def train_and_register(dataset_path: str) -> str:
        if not dataset_path:
            raise ValueError("dataset artifact path is required")
        return str(train_stage())

    @task(retries=1)
    def quality_gate_and_promote(candidate_path: str) -> str:
        if not candidate_path:
            raise ValueError("candidate artifact path is required")
        return promote_stage().reason

    quality_gate_and_promote(train_and_register(generate_and_validate()))


mlops_pipeline = build_pipeline()

if __name__ == "__main__":
    mlops_pipeline.test()

