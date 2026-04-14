"""Executor LLM — picks one step from an approved plan and runs it."""

from __future__ import annotations

import logging

from ..action import Action
from ..types import Plan, Step

logger = logging.getLogger("ares.cognition.executor")


class Executor:
    def __init__(self, action: Action):
        self.action = action

    def pick_next_step(self, plan: Plan) -> Step | None:
        for step in plan.steps:
            if not step.completed:
                return step
        return None

    def execute(self, step: Step) -> str:
        logger.info("executing step %d: %s (%s)", step.index, step.description, step.tool)
        try:
            outcome = self.action.dispatch(step.tool, step.arguments)
            step.outcome = outcome
            return outcome
        except Exception as exc:
            msg = f"error: {exc}"
            step.outcome = msg
            logger.warning("step %d failed: %s", step.index, msg)
            return msg
