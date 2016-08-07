import pytest


@pytest.fixture
def klass():
    from agile_analytics import CreatedReporter
    return CreatedReporter


def test_klass(klass):
    assert klass


def test_filter(klass, days_agos, AnalyzedAgileTicket):
    """filter_issues ignores issues completed before the specified range."""
    issue_list_kwargs = []
    for i in range(1, 3):
        kwargs = dict(
            key="TEST-{}".format(i),
            committed=dict(state="Committed", entered_at=days_agos[2]),
            started=dict(state=None, entered_at=None),
            ended=dict(state=None, entered_at=None)
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
        title="Issues Created in last 30 day",
        start_date=days_agos[30],
        end_date=days_agos[0]
    )
    filtered_issues = r.filter_issues(issue_list)

    assert r.start_date > issue_out_of_range.ended['entered_at']
    assert len(filtered_issues) == 2


def test_report(klass, weeks_of_tickets, date, datetime, tzutc):
    """Report should return counts per week per ticket type"""

    r = klass(
        title="Lead Time Percentile Report",
        start_date=datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc),  # Sunday
        end_date=datetime(2016, 7, 2, 11, 59, 59, tzinfo=tzutc),  # Saturday
    )

    expected = [
        ["Week", "Ticket"],
        [date(2016, 5, 15), 0],
        [date(2016, 5, 22), 3],
        [date(2016, 5, 29), 4],
        [date(2016, 6, 5), 1],
        [date(2016, 6, 12), 8],
        [date(2016, 6, 19), 1],
        [date(2016, 6, 26), 0],
    ]

    assert r.report_on(weeks_of_tickets).table == expected
