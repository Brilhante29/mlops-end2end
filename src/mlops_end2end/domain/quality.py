from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateMetrics:
    run_id: str
    model_version: str
    roc_auc: float
    accuracy: float

    def __post_init__(self) -> None:
        for name, value in (("roc_auc", self.roc_auc), ("accuracy", self.accuracy)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class PromotionDecision:
    approved: bool
    reason: str


@dataclass(frozen=True)
class QualityPolicy:
    minimum_roc_auc: float

    def decide(self, candidate: CandidateMetrics) -> PromotionDecision:
        if candidate.roc_auc >= self.minimum_roc_auc:
            return PromotionDecision(
                approved=True,
                reason=(
                    f"roc_auc={candidate.roc_auc:.4f} meets "
                    f"minimum={self.minimum_roc_auc:.4f}"
                ),
            )
        return PromotionDecision(
            approved=False,
            reason=(
                f"roc_auc={candidate.roc_auc:.4f} is below "
                f"minimum={self.minimum_roc_auc:.4f}"
            ),
        )

