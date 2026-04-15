"""Critic LLM — reviews plans, verifies step outcomes, refuses bad goals."""

from __future__ import annotations

import logging

from openai import OpenAI

from ..config import settings
from ..types import Goal, Plan, Step

logger = logging.getLogger("ares.cognition.critic")


CRITIC_SYSTEM = """\
You are the CRITIC inside ARES, an autonomous digital worker.

You do not plan. You do not execute. You review.

When reviewing a PLAN, output exactly one of:
  APPROVE
  REFUSE: <one-line reason>
  REVISE: <one-line reason>

When verifying a STEP OUTCOME, output exactly one of:
  OK
  FAIL: <one-line reason>

Refuse plans that are: unsafe, illegal, out-of-scope, uneconomic, or that
violate the reputation policy.

Do not narrate. Output only the verdict.
"""


class Critic:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def review_plan(self, goal: Goal, plan: Plan) -> str:
        user = (
            f"GOAL: {goal.description}\n\n"
            f"PLAN:\n"
            + "\n".join(f"{s.index}. [{s.tool}] {s.description}" for s in plan.steps)
        )
        verdict = self._ask(user)
        if verdict.startswith("APPROVE"):
            plan.approved = True
        elif verdict.startswith("REFUSE"):
            plan.refused = True
            plan.critic_notes = verdict
        else:
            plan.critic_notes = verdict
        return verdict

    def verify_step(self, step: Step) -> bool:
        user = (
            f"STEP: {step.description}\n"
            f"TOOL: {step.tool}\n"
            f"SUCCESS CRITERION: {step.success_criterion}\n"
            f"OUTCOME: {step.outcome}"
        )
        verdict = self._ask(user)
        return verdict.startswith("OK")

    def _ask(self, user: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": CRITIC_SYSTEM},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
