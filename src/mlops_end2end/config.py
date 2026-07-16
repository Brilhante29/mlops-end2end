from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    runtime_dir: Path
    tracking_uri: str
    model_name: str = "portfolio-risk-model"
    model_alias: str = "champion"
    quality_threshold: float = 0.80
    random_seed: int = 42
    sample_count: int = 1_200
    feature_count: int = 8

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            runtime_dir=Path(os.getenv("MLOPS_RUNTIME_DIR", "/tmp/mlops-end2end")),
            tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"),
            model_name=os.getenv("MODEL_NAME", "portfolio-risk-model"),
            model_alias=os.getenv("MODEL_ALIAS", "champion"),
            quality_threshold=float(os.getenv("QUALITY_THRESHOLD", "0.80")),
            random_seed=int(os.getenv("RANDOM_SEED", "42")),
            sample_count=int(os.getenv("SAMPLE_COUNT", "1200")),
            feature_count=int(os.getenv("FEATURE_COUNT", "8")),
        )

    @property
    def data_dir(self) -> Path:
        return self.runtime_dir / "data"

    @property
    def dataset_path(self) -> Path:
        return self.data_dir / "classification.csv"

    @property
    def candidate_path(self) -> Path:
        return self.runtime_dir / "candidate.json"

    def prepare(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

