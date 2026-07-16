from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from mlops_end2end.api import ModelState, PredictionRequest
from mlops_end2end.config import Settings


class ProbabilityModel:
    def predict(self, _):
        return np.asarray([[0.18, 0.82]])


def test_prediction_contract_requires_exact_feature_count() -> None:
    with pytest.raises(ValidationError, match="exactly 8"):
        PredictionRequest(features=[0.1, 0.2])


def test_model_state_maps_probability_to_response(tmp_path) -> None:
    state = ModelState(model=ProbabilityModel(), version="3")
    settings = Settings(runtime_dir=tmp_path, tracking_uri="http://unused")
    response = state.predict([0.0] * 8, settings)
    assert response.prediction == 1
    assert response.probability == pytest.approx(0.82)
    assert response.model_version == "3"
