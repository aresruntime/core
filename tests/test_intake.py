"""Intake parsing."""

from ares.commerce.intake import JobIntake
from ares.types import GoalSource, Percept


def test_parse_valid_percept():
    p = Percept(source="intake", payload={
        "goal": "research AI agents",
        "deliverable": "markdown",
        "price_sol": 0.25,
        "return_address": "Abc...",
    })
    goal = JobIntake.parse(p)
    assert goal is not None
    assert goal.source == GoalSource.ASSIGNED
    assert goal.price_sol == 0.25
    assert goal.is_paid is True


def test_parse_wrong_source():
    p = Percept(source="email", payload={"goal": "x"})
    assert JobIntake.parse(p) is None


def test_parse_missing_goal_field():
    p = Percept(source="intake", payload={"description": "x"})
    assert JobIntake.parse(p) is None
