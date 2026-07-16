from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from sklearn.datasets import make_classification

from mlops_end2end.config import Settings


def feature_names(feature_count: int) -> list[str]:
    return [f"feature_{index}" for index in range(feature_count)]


def dataset_schema(feature_count: int) -> pa.DataFrameSchema:
    columns: dict[str, pa.Column] = {
        name: pa.Column(float, nullable=False) for name in feature_names(feature_count)
    }
    columns["target"] = pa.Column(int, checks=pa.Check.isin([0, 1]), nullable=False)
    return pa.DataFrameSchema(columns, strict=True, coerce=True)


def generate_dataset(settings: Settings) -> Path:
    settings.prepare()
    features, target = make_classification(
        n_samples=settings.sample_count,
        n_features=settings.feature_count,
        n_informative=6,
        n_redundant=1,
        class_sep=1.25,
        random_state=settings.random_seed,
    )
    frame = pd.DataFrame(features, columns=feature_names(settings.feature_count))
    frame["target"] = target
    validated = dataset_schema(settings.feature_count).validate(frame)
    validated.to_csv(settings.dataset_path, index=False)
    return settings.dataset_path


def load_validated_dataset(path: Path, feature_count: int) -> pd.DataFrame:
    frame = pd.read_csv(path)
    return dataset_schema(feature_count).validate(frame)

