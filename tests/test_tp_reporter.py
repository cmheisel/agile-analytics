"""Test ThroughputReporter"""

import pytest


@pytest.fixture
def klass():
    """Return CUT."""
    from agile_analytics import ThroughputReporter
    return ThroughputReporter


def test_title(klass):
    """Ensure the title gets set."""
    r = klass(
        title="Weekly Throughput"
    )
    assert r.title == "Weekly Throughput"


def test_period(klass):
    """Ensure the period can be set."""
    r = klass(title="Weekly Throughput")
    r.period = "weekly"
    assert r.period == "weekly"


def test_date_assignment(klass, days_ago):
    """Ensure the range can be set."""
    r = klass(title="Weekly Throughput")
    r.start_date = days_ago(30)
    r.end_date = days_ago(0)

    assert r.start_date == days_ago(30)
    assert r.end_date == days_ago(0)


def test_date_range_reconcile(klass, datetime):
    """Ensure the right dates are set when passed two dates and a weekly period arg."""
    r = klass(title="Weekly Throughput")
    r.period = "weekly"
    r.start_date = datetime(2016, 5, 21, 0, 0, 0)
    r.end_date = datetime(2016, 6, 21, 11, 59, 59)

    assert r.start_date == datetime(2016, 5, 15, 0, 0, 0)  # Sunday
    assert r.end_date == datetime(2016, 6, 25, 11, 59, 59)  # Saturday


def test_date_reconcile_post_hoc(klass, datetime):
    """When you set the period after the dates, the dates should be adjusted."""
    r = klass(title="Weekly Throughput")
    r.start_date = datetime(2016, 5, 21, 0, 0, 0)
    r.end_date = datetime(2016, 6, 21, 11, 59, 59)
    r.period = "weekly"

    assert r.start_date == datetime(2016, 5, 15, 0, 0, 0)  # Sunday
    assert r.end_date == datetime(2016, 6, 25, 11, 59, 59)  # Saturday
