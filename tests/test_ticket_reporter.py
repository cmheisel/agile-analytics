"""Test the TicketReporter class."""

import pytest


@pytest.fixture
def klass():
    """Return the CUT."""
    from agile_analytics import TicketReporter
    return TicketReporter


def test_klass(klass):
    """Verify the CUT fixture."""
    assert klass


def test_klass_init(klass):
    """Verify init."""
    r = klass(
        title="Foo"
    )
    assert r


def test_date_range_reconcile(klass, datetime, tzutc):
    """Ensure the right dates are set when passed two dates."""
    r = klass(title="Foo")
    r.start_date = datetime(2016, 5, 21, 0, 0, 0)
    r.end_date = datetime(2016, 6, 21, 11, 59, 59)

    assert r.start_date == datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc)  # Sunday
    assert r.end_date == datetime(2016, 6, 25, 11, 59, 59, tzinfo=tzutc)  # Saturday


def test_filter(klass, days_agos, AnalyzedAgileTicket):
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


def test_report_table(klass, AnalyzedAgileTicket, days_agos):
    """Ensure the report table returns a row with details on every ticket."""

    issue_list_kwargs = []
    for i in range(1, 3):  # 2 issues with 2 day lead
        kwargs = dict(
            key="TEST-{}".format(i),
            committed=dict(state="Committed", entered_at=days_agos[i+3]),
            started=dict(state="Started", entered_at=days_agos[i+2]),
            ended=dict(state="Ended", entered_at=days_agos[i]),
        )
        issue_list_kwargs.append(kwargs)
    issue_list = [AnalyzedAgileTicket(**kwargs) for kwargs in issue_list_kwargs]
    issue_list.sort(key=lambda i: i.ended['entered_at'])

    expected = [
        ["Key", "Lead Time", "Commit State", "Commit At", "Start State", "Start At", "End State", "End At"],
    ]
    for i in issue_list:
        row = [
            i.key,
            i.lead_time,
            i.committed['state'],
            i.committed['entered_at'],
            i.started['state'],
            i.started['entered_at'],
            i.ended['state'],
            i.ended['entered_at'],
        ]
        expected.append(row)

    r = klass(
        title="Cycle Time Distribution Past 30 days",
        start_date=days_agos[30],
        end_date=days_agos[0]
    )

    actual = r.report_on(issue_list)
    assert expected == actual.table


def test_report_summary(klass, datetime, tzutc):
    """report_on returns an object with meta data."""
    start_date = datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc)  # Sunday
    end_date = datetime(2016, 6, 25, 11, 59, 59, tzinfo=tzutc)  # Saturday

    r = klass(
        title="Foo",
        start_date=start_date,
        end_date=end_date
    )

    expected = dict(
        title="Foo",
        start_date=start_date,
        end_date=end_date,
    )

    assert r.report_on([]).summary == expected
