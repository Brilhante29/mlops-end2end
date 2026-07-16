from __future__ import annotations

import json
from pathlib import Path

from mlops_end2end.adapters.data import generate_dataset
from mlops_end2end.adapters.mlflow_registry import MlflowModelRegistry
from mlops_end2end.adapters.training import train_candidate
from mlops_end2end.application.promotion import promote_candidate
from mlops_end2end.config import Settings
from mlops_end2end.domain import CandidateMetrics, PromotionDecision, QualityPolicy


def generate_stage(settings: Settings | None = None) -> Path:
    return generate_dataset(settings or Settings.from_env())


def train_stage(settings: Settings | None = None) -> Path:
    active_settings = settings or Settings.from_env()
    train_candidate(active_settings)
    return active_settings.candidate_path


def promote_stage(settings: Settings | None = None) -> PromotionDecision:
    active_settings = settings or Settings.from_env()
    payload = json.loads(active_settings.candidate_path.read_text(encoding="utf-8"))
    candidate = CandidateMetrics(**payload)
    return promote_candidate(
        candidate=candidate,
        policy=QualityPolicy(active_settings.quality_threshold),
        registry=MlflowModelRegistry(
            tracking_uri=active_settings.tracking_uri,
            model_name=active_settings.model_name,
        ),
        alias=active_settings.model_alias,
    )

