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


def test_filter(klass, days_agos, AnalyzedAgileTicket, tzutc):
    """filter_issues ignores issues completed before the specified range."""
    issue_list_kwargs = []
    for i in range(1, 3):  # 2 issues with 2 day lead
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
        committed=dict(state="Committed", entered_at=days_agos[42]),
        started=dict(state="Started", entered_at=days_agos[44]),
        ended=dict(state="Ended", entered_at=days_agos[45]),
    )
    issue_list.append(issue_out_of_range)

    r = klass(
        title="Cycle Time Distribution Past 30 days",
        start_date=days_agos[30],
        end_date=days_agos[0]
    )
    filtered_issues = r.filter_issues(issue_list)

    assert r.start_date > issue_out_of_range.ended['entered_at']
    assert len(filtered_issues) == 2


def test_report_summary(klass, datetime, tzutc):
    """report_on returns an object with meta data."""
    start_date = datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc)  # Sunday
    end_date = datetime(2016, 6, 25, 11, 59, 59, tzinfo=tzutc)  # Saturday

    r = klass(
        title="Cycle Time Distribution Past 30 days",
        start_date=start_date,
        end_date=end_date
    )

    expected = dict(
        title="Cycle Time Distribution Past 30 days",
        start_date=start_date,
        end_date=end_date,
    )

    assert r.report_on([]).summary == expected


def test_report_table_empty(klass, days_agos):
    """Ensure an empty list of tickets is handled."""
    expected = [
        ["Lead Time", "Tickets"]
    ]
    r = klass(
        title="Cycle Time Distribution Past 30 days",
        start_date=days_agos[30],
        end_date=days_agos[0]
    )

    report = r.report_on([])

    assert report.table == expected


def test_report_table(klass, days_agos, AnalyzedAgileTicket, tzutc):
    """report_on returns an object with a tabular represenation of the data"""
    issue_list_kwargs = []
    for i in range(1, 3):  # 2 issues with 2 day lead
        kwargs = dict(
            key="TEST-{}".format(i),
            committed=dict(state="Committed", entered_at=days_agos[2]),
            started=dict(state="Started", entered_at=days_agos[2]),
            ended=dict(state="Ended", entered_at=days_agos[0]),
        )
        issue_list_kwargs.append(kwargs)

    for i in range(4, 10):  # 6 issues, with 5 day lead
        kwargs = dict(
            key="TEST-{}".format(i),
            committed=dict(state="Committed", entered_at=days_agos[5]),
            started=dict(state="Started", entered_at=days_agos[4]),
            ended=dict(state="Ended", entered_at=days_agos[0]),
        )
        issue_list_kwargs.append(kwargs)

    for i in range(11, 13):  # 2 issues, with 10 day lead
        kwargs = dict(
            key="TEST-{}".format(i),
            committed=dict(state="Committed", entered_at=days_agos[10]),
            started=dict(state="Started", entered_at=days_agos[9]),
            ended=dict(state="Ended", entered_at=days_agos[0]),
        )
        issue_list_kwargs.append(kwargs)

    issue_list = [AnalyzedAgileTicket(**kwargs) for kwargs in issue_list_kwargs]

    expected = [
        ["Lead Time", "Tickets"],
        [1, 0],
        [2, 2],
        [3, 0],
        [4, 0],
        [5, 6],
        [6, 0],
        [7, 0],
        [8, 0],
        [9, 0],
        [10, 2]
    ]
    r = klass(
        title="Cycle Time Distribution Past 30 days",
        start_date=days_agos[30],
        end_date=days_agos[0]
    )

    report = r.report_on(issue_list)

    assert report.table == expected
