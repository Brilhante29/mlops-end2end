from __future__ import annotations

from mlflow import MlflowClient

from mlops_end2end.domain import CandidateMetrics


class MlflowModelRegistry:
    def __init__(self, tracking_uri: str, model_name: str) -> None:
        self._client = MlflowClient(tracking_uri=tracking_uri)
        self._model_name = model_name

    def promote(self, candidate: CandidateMetrics, alias: str) -> None:
        self._client.set_model_version_tag(
            self._model_name,
            candidate.model_version,
            "validation_status",
            "approved",
        )
        self._client.set_model_version_tag(
            self._model_name,
            candidate.model_version,
            "roc_auc",
            f"{candidate.roc_auc:.6f}",
        )
        self._client.set_registered_model_alias(
            self._model_name,
            alias,
            candidate.model_version,
        )

