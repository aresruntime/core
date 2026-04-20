"""Reputation tracker — per-platform scores."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Reputation:
    jobs_completed: int = 0
    jobs_refused: int = 0
    jobs_failed: int = 0
    total_earned_sol: float = 0.0
    average_delivery_hours: float = 0.0
    per_platform_scores: dict = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        total = self.jobs_completed + self.jobs_failed
        return self.jobs_completed / total if total > 0 else 0.0

    def record_completion(self, price_sol: float, delivery_hours: float) -> None:
        n = self.jobs_completed
        self.jobs_completed += 1
        self.total_earned_sol += price_sol
        if n == 0:
            self.average_delivery_hours = delivery_hours
        else:
            self.average_delivery_hours = (
                (self.average_delivery_hours * n + delivery_hours) / (n + 1)
            )

    def record_failure(self) -> None:
        self.jobs_failed += 1

    def record_refusal(self) -> None:
        self.jobs_refused += 1
