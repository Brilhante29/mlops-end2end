from __future__ import annotations

from mlops_end2end.application.ports import ModelRegistryPort
from mlops_end2end.domain import CandidateMetrics, PromotionDecision, QualityPolicy


class QualityGateRejected(RuntimeError):
    pass


def promote_candidate(
    candidate: CandidateMetrics,
    policy: QualityPolicy,
    registry: ModelRegistryPort,
    alias: str,
) -> PromotionDecision:
    decision = policy.decide(candidate)
    if not decision.approved:
        raise QualityGateRejected(decision.reason)
    registry.promote(candidate, alias)
    return decision

