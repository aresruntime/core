"""Reputation metrics."""

from ares.reputation import Reputation


def test_success_rate_zero_when_no_history():
    r = Reputation()
    assert r.success_rate == 0.0


def test_success_rate_after_mixed_history():
    r = Reputation()
    r.record_completion(0.1, 2.0)
    r.record_completion(0.2, 3.0)
    r.record_failure()
    assert abs(r.success_rate - 2/3) < 1e-6


def test_average_delivery_hours():
    r = Reputation()
    r.record_completion(0.1, 4.0)
    r.record_completion(0.1, 6.0)
    assert r.average_delivery_hours == 5.0
