from __future__ import annotations

from typing import Protocol

from mlops_end2end.domain import CandidateMetrics


class ModelRegistryPort(Protocol):
    def promote(self, candidate: CandidateMetrics, alias: str) -> None: ...

