"""Test Lead Time reporter."""

import pytest


@pytest.fixture
def AnalyzedAgileTicket():
    """Return a class used by the CUT."""
    from agile_analytics.models import AnalyzedAgileTicket
    return AnalyzedAgileTicket


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


def test_filter(klass, days_ago, AnalyzedAgileTicket, tzutc):
    """filter_issues ignores issues completed before the specified range."""
    days_agos = {}
    for i in range(0, 35):
        days_agos[i] = days_ago(i)

    issue_list_kwargs = []
    for i in range(1, 3):
        kwargs = dict(
            key="TEST-{}".format(i),
            committed=dict(state="Committed", entered_at=days_agos[2]),
            started=dict(state="Started", entered_at=days_agos[2]),
            ended=dict(state="Ended", entered_at=days_agos[0]),
        )
        issue_list_kwargs.append(kwargs)

    issue_list = [AnalyzedAgileTicket(**kwargs) for kwargs in issue_list_kwargs]
    issue_out_of_range = AnalyzedAgileTicket(
        key="TEST-OOR",
        committed=dict(state="Committed", entered_at=days_agos[34]),
        started=dict(state="Started", entered_at=days_agos[33]),
        ended=dict(state="Ended", entered_at=days_agos[31]),
    )
    issue_list.append(issue_out_of_range)

    r = klass(
        title="Cycle Time Distribution Past 30 days",
        start_date=days_ago(30),
        end_date=days_ago(0)
    )
    assert len(r.filter_issues(issue_list)) == 3
