"""Planner LLM — decomposes goals into 1-12 steps."""

from __future__ import annotations

import json
import logging
import uuid

from anthropic import Anthropic

from ..config import settings
from ..types import Goal, Plan, Step

logger = logging.getLogger("ares.cognition.planner")


PLANNER_SYSTEM = """\
You are the PLANNER inside ARES, an autonomous digital worker.

Your job: given a goal, produce a step-by-step plan of 1-12 concrete actions
that achieve it. Each step must specify a tool and arguments.

Available tools:
- browser.navigate(url)
- browser.click(selector)
- browser.type(selector, text)
- browser.extract(selector_or_instruction)
- http.get(url, headers?)
- http.post(url, body, headers?)
- terminal.run(command)
- fs.read(path) / fs.write(path, content)
- wallet.pay(address, amount_sol, memo?)
- wallet.balance()
- memory.query(semantic_query) / memory.write(key, value)
- delegate.hire(goal_description, max_price_sol)

Return ONLY valid JSON matching this schema:
{
  "steps": [
    { "description": "...", "tool": "...", "arguments": {...}, "success_criterion": "..." }
  ]
}

Do not include prose. Do not include the goal text. Only the JSON object.
"""


class Planner:
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def plan(self, goal: Goal, context: str = "") -> Plan:
        prompt = f"GOAL:\n{goal.description}\n\nCONTEXT:\n{context or '(none)'}"
        logger.info("planning goal %s", goal.id)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=PLANNER_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.error("planner returned invalid JSON; refusing plan")
            return Plan(goal_id=goal.id, steps=[], refused=True, critic_notes="invalid json from planner")

        steps = [
            Step(
                index=i,
                description=s["description"],
                tool=s["tool"],
                arguments=s.get("arguments", {}),
                success_criterion=s.get("success_criterion", ""),
            )
            for i, s in enumerate(data.get("steps", []))
        ]
        return Plan(goal_id=goal.id, steps=steps, approved=False)


def new_goal_id() -> str:
    return uuid.uuid4().hex[:12]
