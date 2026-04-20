"""Survival layer — compute budget, solvency transitions, dormancy."""

from __future__ import annotations

import logging

from .config import settings
from .types import GoalSource, RuntimeState, SolvencyState

logger = logging.getLogger("ares.survival")


LAMPORTS_PER_SOL = 1_000_000_000
# Rough SOL price — real impl reads from an oracle.
ASSUMED_SOL_PRICE_USD = 150.0


class Survival:
    """Computes solvency state and recommends next-goal source."""

    def __init__(self, wallet):
        self.wallet = wallet

    def update(self, state: RuntimeState) -> RuntimeState:
        balance = self.wallet.balance()
        state.wallet_balance_lamports = balance
        usd = balance / LAMPORTS_PER_SOL * ASSUMED_SOL_PRICE_USD

        if usd <= 0.0:
            state.solvency = SolvencyState.DORMANT
        elif usd < settings.ares_dormancy_threshold_usd:
            state.solvency = SolvencyState.HUSTLING
        else:
            state.solvency = SolvencyState.SOLVENT

        logger.info(
            "survival: balance=%d lamports (~$%.2f) state=%s",
            balance, usd, state.solvency.value,
        )
        return state

    def recommend_source(self, state: RuntimeState) -> GoalSource:
        if state.solvency in (SolvencyState.HUSTLING, SolvencyState.DORMANT):
            return GoalSource.ASSIGNED
        return GoalSource.SELF
