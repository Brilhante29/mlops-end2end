from __future__ import annotations

import pytest

from mlops_end2end.application.promotion import QualityGateRejected, promote_candidate
from mlops_end2end.domain import CandidateMetrics, QualityPolicy


class RecordingRegistry:
    def __init__(self) -> None:
        self.promotions: list[tuple[str, str]] = []

    def promote(self, candidate: CandidateMetrics, alias: str) -> None:
        self.promotions.append((candidate.model_version, alias))


def candidate(roc_auc: float) -> CandidateMetrics:
    return CandidateMetrics(
        run_id="run-1",
        model_version="7",
        roc_auc=roc_auc,
        accuracy=0.84,
    )


def test_approved_candidate_is_promoted_through_port() -> None:
    registry = RecordingRegistry()
    decision = promote_candidate(
        candidate(0.91), QualityPolicy(0.80), registry, "champion"
    )
    assert decision.approved is True
    assert registry.promotions == [("7", "champion")]


def test_rejected_candidate_never_reaches_registry() -> None:
    registry = RecordingRegistry()
    with pytest.raises(QualityGateRejected, match="below"):
        promote_candidate(candidate(0.72), QualityPolicy(0.80), registry, "champion")
    assert registry.promotions == []


@pytest.mark.parametrize("metric", [-0.1, 1.1])
def test_candidate_metrics_reject_invalid_probabilities(metric: float) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        candidate(metric)
