"""Job intake — parses incoming job specs and turns them into Goals."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from ..types import Goal, GoalSource, Percept

logger = logging.getLogger("ares.intake")


class JobIntake:
    """Converts a Percept from the intake surface into a Goal."""

    @staticmethod
    def parse(percept: Percept) -> Goal | None:
        if percept.source != "intake":
            return None
        p = percept.payload
        if "goal" not in p:
            logger.warning("intake percept missing 'goal' field")
            return None
        return Goal(
            id=uuid.uuid4().hex[:12],
            description=p["goal"],
            source=GoalSource.ASSIGNED,
            deliverable=p.get("deliverable"),
            price_sol=float(p.get("price_sol", 0.0)),
            requester=p.get("return_address"),
            deadline=_parse_deadline(p.get("deadline")),
        )


def _parse_deadline(raw) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
