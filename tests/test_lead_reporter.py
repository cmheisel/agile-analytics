"""Test Lead Time reporter."""

import pytest


@pytest.fixture
def klass():
    """Provide the CUT."""
    from agile_analytics import LeadTimeDistributionReporter
    return LeadTimeDistributionReporter


def test_klass(klass):
    """Ensure the fixture works."""
    assert klass


def test_date_selection(klass, datetime, tzutc):
    """Ensure the CUT picks Sunday-Saturday date range"""
    r = klass("Foo")
    r.start_date = datetime(2016, 5, 21, 0, 0, 0)
    r.end_date = datetime(2016, 6, 21, 11, 59, 59)

    assert r.start_date == datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc)  # Sunday
    assert r.end_date == datetime(2016, 6, 25, 11, 59, 59, tzinfo=tzutc)  # Saturday
