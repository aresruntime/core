"""Survival layer transitions."""

from ares.types import GoalSource, RuntimeState, SolvencyState


class _FakeWallet:
    def __init__(self, lamports: int): self._l = lamports
    def balance(self): return self._l


def test_hustling_below_threshold():
    from ares.survival import Survival
    s = Survival(_FakeWallet(1_000_000))  # 0.001 SOL ≈ $0.15
    state = s.update(RuntimeState())
    assert state.solvency == SolvencyState.HUSTLING


def test_solvent_above_threshold():
    from ares.survival import Survival
    s = Survival(_FakeWallet(500_000_000))  # 0.5 SOL ≈ $75
    state = s.update(RuntimeState())
    assert state.solvency == SolvencyState.SOLVENT


def test_dormant_at_zero():
    from ares.survival import Survival
    s = Survival(_FakeWallet(0))
    state = s.update(RuntimeState())
    assert state.solvency == SolvencyState.DORMANT


def test_hustling_prefers_assigned_source():
    from ares.survival import Survival
    s = Survival(_FakeWallet(1_000))
    state = RuntimeState(solvency=SolvencyState.HUSTLING)
    assert s.recommend_source(state) == GoalSource.ASSIGNED
