"""Unified perception reader — the first step of every tick."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import httpx

from ..config import settings
from ..types import Percept, RuntimeState

logger = logging.getLogger("ares.perception")


class Perception:
    """Reads from every configured surface, returns a list of percepts."""

    def __init__(self, jobs_path: str | None = None):
        self.jobs_path = Path(jobs_path or settings.ares_jobs_path)
        self.jobs_path.mkdir(parents=True, exist_ok=True)

    def read(self, state: RuntimeState) -> list[Percept]:
        percepts: list[Percept] = []
        percepts.extend(self._read_intake())
        percepts.extend(self._read_email())
        percepts.extend(self._read_mentions())
        percepts.extend(self._read_github())
        logger.info("perceived %d new items this tick", len(percepts))
        return percepts

    # ── per-surface readers ────────────────────────────────

    def _read_intake(self) -> list[Percept]:
        """Read any new job files dropped into the intake directory."""
        out: list[Percept] = []
        inbox = self.jobs_path / "intake"
        inbox.mkdir(parents=True, exist_ok=True)
        for path in inbox.glob("*.json"):
            try:
                data = __import__("json").loads(path.read_text(encoding="utf-8"))
                out.append(Percept(source="intake", payload=data))
                path.rename(inbox / "_consumed" / path.name)
            except Exception as exc:
                logger.warning("intake read failed: %s %s", path, exc)
        return out

    def _read_email(self) -> list[Percept]:
        if not settings.ares_email:
            return []
        # Placeholder — production would use IMAP or a service API.
        return []

    def _read_mentions(self) -> list[Percept]:
        if not settings.ares_x_bearer:
            return []
        try:
            with httpx.Client(timeout=10) as client:
                # Real implementation uses Twitter v2 /users/:id/mentions.
                # Stubbed here to keep the runtime hermetic.
                return []
        except Exception as exc:
            logger.warning("x mentions read failed: %s", exc)
            return []

    def _read_github(self) -> list[Percept]:
        if not settings.ares_github_token:
            return []
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(
                    "https://api.github.com/notifications",
                    headers={"Authorization": f"Bearer {settings.ares_github_token}"},
                )
                if r.status_code == 200:
                    return [Percept(source="github", payload={"notifications": r.json()})]
                return []
        except Exception as exc:
            logger.warning("github read failed: %s", exc)
            return []
