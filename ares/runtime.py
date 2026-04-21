"""The main runtime. One tick = one pass of the eight-step loop."""

from __future__ import annotations

import logging
import time
from datetime import datetime

from .action import Action
from .action.browser import Browser
from .cognition import Critic, Executor, Planner
from .commerce.intake import JobIntake
from .commerce.wallet import Wallet
from .commerce.x402 import X402Client
from .config import settings
from .memory import Memory
from .perception import Perception
from .reputation import Reputation
from .survival import Survival
from .types import Goal, GoalSource, Percept, RuntimeState

logger = logging.getLogger("ares.runtime")


class Runtime:
    """Assembles all layers and runs the ARES loop."""

    def __init__(self):
        self.memory = Memory()
        self.wallet = Wallet()
        self.browser = Browser()
        self.action = Action(browser=self.browser, wallet=self.wallet, memory=self.memory)
        self.planner = Planner()
        self.executor = Executor(self.action)
        self.critic = Critic()
        self.perception = Perception()
        self.survival = Survival(self.wallet)
        self.x402 = X402Client(self.wallet)
        self.reputation = Reputation()

    # ── the tick ───────────────────────────────────────

    def tick(self) -> dict:
        state = self.memory.load_state()
        state.tick += 1
        state.last_tick_at = datetime.utcnow()
        logger.info("=== TICK %d ===", state.tick)

        # 1. PERCEIVE
        percepts = self.perception.read(state)
        for p in percepts:
            self._ingest(p)

        # 8. SURVIVE (run early — informs INTEND)
        state = self.survival.update(state)

        # 2. INTEND
        prefer_paid = self.survival.recommend_source(state) == GoalSource.ASSIGNED
        goal = self.memory.next_pending_goal(prefer_paid=prefer_paid)
        if goal is None:
            state.consecutive_idle_ticks += 1
            self.memory.save_state(state)
            return {"tick": state.tick, "goal": None, "reason": "idle"}

        state.current_goal_id = goal.id
        state.consecutive_idle_ticks = 0

        # 3. PLAN
        plan = self.planner.plan(goal)
        self.critic.review_plan(goal, plan)
        if plan.refused:
            goal.refused = True
            goal.refusal_reason = plan.critic_notes
            self.memory.write_goal(goal)
            self.reputation.record_refusal()
            self.memory.save_state(state)
            return {"tick": state.tick, "goal": goal.id, "refused": True}

        # 4. ACT — one step per tick
        step = self.executor.pick_next_step(plan)
        if step is None:
            goal.completed = True
            self.memory.write_goal(goal)
            self.memory.save_state(state)
            return {"tick": state.tick, "goal": goal.id, "completed": True}

        outcome = self.executor.execute(step)

        # 5. VERIFY
        ok = self.critic.verify_step(step)
        step.completed = ok

        # 6. RECORD
        self.memory.record_step(goal.id, step.index, step.tool, step.arguments, outcome, ok)

        # 7. EARN
        if goal.completed and goal.is_paid:
            self.memory.record_ledger("in", goal.price_sol, counterparty=goal.requester, memo=f"job:{goal.id}")
            self.reputation.record_completion(goal.price_sol, delivery_hours=0.0)

        self.memory.save_state(state)
        return {
            "tick": state.tick,
            "goal": goal.id,
            "step": step.index,
            "tool": step.tool,
            "ok": ok,
            "outcome": outcome[:200],
        }

    def run_forever(self) -> None:
        while True:
            try:
                self.tick()
            except KeyboardInterrupt:
                logger.info("operator stopped the runtime.")
                break
            except Exception as exc:
                logger.exception("tick error: %s", exc)
            time.sleep(settings.ares_tick_interval)

    # ── internal ───────────────────────────────────────

    def _ingest(self, percept: Percept) -> None:
        if percept.source == "intake":
            goal = JobIntake.parse(percept)
            if goal is not None:
                self.memory.write_goal(goal)
                logger.info("new assigned goal: %s", goal.id)
