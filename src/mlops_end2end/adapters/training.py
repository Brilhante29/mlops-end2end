from __future__ import annotations

import json
from dataclasses import asdict

import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mlops_end2end.adapters.data import feature_names, load_validated_dataset
from mlops_end2end.config import Settings
from mlops_end2end.domain import CandidateMetrics


def _registered_version(client: MlflowClient, model_name: str, run_id: str) -> str:
    versions = client.search_model_versions(
        filter_string=f"name='{model_name}' and run_id='{run_id}'",
        max_results=10,
    )
    if not versions:
        raise RuntimeError(f"MLflow did not create a model version for run {run_id}")
    return str(max(versions, key=lambda item: int(item.version)).version)


def train_candidate(settings: Settings) -> CandidateMetrics:
    frame = load_validated_dataset(settings.dataset_path, settings.feature_count)
    features = frame[feature_names(settings.feature_count)]
    target = frame["target"]
    train_x, test_x, train_y, test_y = train_test_split(
        features,
        target,
        test_size=0.25,
        stratify=target,
        random_state=settings.random_seed,
    )

    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=500, random_state=settings.random_seed),
            ),
        ]
    )
    model.fit(train_x, train_y)
    probabilities = model.predict_proba(test_x)[:, 1]
    predictions = model.predict(test_x)
    roc_auc = float(roc_auc_score(test_y, probabilities))
    accuracy = float(accuracy_score(test_y, predictions))

    mlflow.set_tracking_uri(settings.tracking_uri)
    mlflow.set_experiment("portfolio-mlops-end2end")
    with mlflow.start_run(run_name="deterministic-logistic-regression") as run:
        mlflow.log_params(
            {
                "algorithm": "logistic_regression",
                "feature_count": settings.feature_count,
                "random_seed": settings.random_seed,
                "sample_count": settings.sample_count,
            }
        )
        mlflow.log_metrics({"roc_auc": roc_auc, "accuracy": accuracy})
        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=settings.model_name,
            input_example=test_x.head(3),
            pyfunc_predict_fn="predict_proba",
        )
        run_id = run.info.run_id

    client = MlflowClient(tracking_uri=settings.tracking_uri)
    candidate = CandidateMetrics(
        run_id=run_id,
        model_version=_registered_version(client, settings.model_name, run_id),
        roc_auc=roc_auc,
        accuracy=accuracy,
    )
    settings.candidate_path.write_text(
        json.dumps(asdict(candidate), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return candidate

