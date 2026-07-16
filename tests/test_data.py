from __future__ import annotations

import hashlib

import pandas as pd
import pandera.pandas as pa
import pytest

from mlops_end2end.adapters.data import generate_dataset, load_validated_dataset
from mlops_end2end.config import Settings


def settings_for(tmp_path) -> Settings:
    return Settings(runtime_dir=tmp_path, tracking_uri="http://unused", sample_count=120)


def test_dataset_generation_is_deterministic(tmp_path) -> None:
    settings = settings_for(tmp_path)
    first = hashlib.sha256(generate_dataset(settings).read_bytes()).hexdigest()
    second = hashlib.sha256(generate_dataset(settings).read_bytes()).hexdigest()
    assert first == second
    frame = load_validated_dataset(settings.dataset_path, settings.feature_count)
    assert len(frame) == 120
    assert set(frame["target"].unique()) == {0, 1}


def test_data_contract_rejects_unknown_target(tmp_path) -> None:
    settings = settings_for(tmp_path)
    path = generate_dataset(settings)
    frame = pd.read_csv(path)
    frame.loc[0, "target"] = 9
    frame.to_csv(path, index=False)
    with pytest.raises(pa.errors.SchemaError):
        load_validated_dataset(path, settings.feature_count)

