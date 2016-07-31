"""Tests for AnalyzedAgileTickets."""

import pytest


@pytest.fixture
def klass():
    from agile_analytics.models import AnalyzedAgileTicket
    return AnalyzedAgileTicket


def test_klass(klass, days_ago):
    """Verify the CUT."""
    assert klass

    five_ago = days_ago(5)
    four_ago = days_ago(4)
    today = days_ago(0)

    k = klass(
        key="TEST-1",
        committed=dict(entered_at=five_ago, state="To Do"),
        started=dict(entered_at=four_ago, state="In Progress"),
        ended=dict(entered_at=today, state="Done"),
    )

    assert k.committed['entered_at'] == five_ago
    assert k.started['entered_at'] == four_ago
    assert k.ended['entered_at'] == today

    assert "{} -- Ended: {}".format(k.key, k.ended['entered_at']) == str(k)


def test_lead_time(klass, days_ago):
    """Verify lead_time calculations."""
    five_ago = days_ago(5)
    four_ago = days_ago(4)
    today = days_ago(0)

    k = klass(
        key="TEST-1",
        committed=dict(entered_at=five_ago, state="To Do"),
        started=dict(entered_at=four_ago, state="In Progress"),
        ended=dict(entered_at=today, state="Done"),
    )

    assert k.lead_time == 5


def test_cycle_time(klass, days_ago):
    """Verify lead_time calculations."""
    five_ago = days_ago(5)
    four_ago = days_ago(4)
    today = days_ago(0)

    k = klass(
        key="TEST-1",
        committed=dict(entered_at=five_ago, state="To Do"),
        started=dict(entered_at=four_ago, state="In Progress"),
        ended=dict(entered_at=today, state="Done"),
    )

    assert k.cycle_time == 4
