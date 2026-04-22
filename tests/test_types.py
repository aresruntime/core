"""Tests for core runtime types."""

from ares.types import Goal, GoalSource, SolvencyState, Step


def test_goal_is_paid():
    assert Goal(id="a", description="x", price_sol=0.5, requester="abc").is_paid is True
    assert Goal(id="a", description="x").is_paid is False


def test_solvency_enum_coverage():
    for s in ("solvent", "hustling", "dormant", "insolvent"):
        assert SolvencyState(s)


def test_step_defaults():
    s = Step(index=0, description="x", tool="http.get")
    assert s.completed is False
    assert s.outcome is None
