import pytest


@pytest.fixture
def klass():
    """Return the CUT."""
    from agile_analytics import CycleTimePercentileReporter
    return CycleTimePercentileReporter


def test_klass(klass):
    """Verify our fixture."""
    assert klass


def test_init(klass, datetime):
    """Make sure it inits the way we want."""
    k = klass(
        title="Cycle Time Percentile Report",
        start_date=datetime(2016, 5, 21, 0, 0, 0),
        end_date=datetime(2016, 6, 21, 11, 59, 59),
        num_weeks=6,
    )
    assert k
    assert k.title == "Cycle Time Percentile Report"
    assert k.num_weeks == 6

    k = klass(
        title="Cycle Time Percentile Report 2",
    )
    assert k
    assert k.title == "Cycle Time Percentile Report 2"
    assert k.num_weeks == 4


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


def test_report_table(klass, weeks_of_tickets, date, datetime, tzutc):
    """Ensure the report table returns a row for every week"""

    expected = [
        ["Week", "50th", "75th", "95th"],
        [date(2016, 5, 15), 4, 7, 12],
        [date(2016, 5, 22), 9, 15, 16],
        [date(2016, 5, 29), 13, 15, 16],
        [date(2016, 6, 5), 14, 16, 17],
        [date(2016, 6, 12), 13, 16, 17],
        [date(2016, 6, 19), 10, 14, 18],
        [date(2016, 6, 26), 10, 15, 18],
    ]

    r = klass(
        title="Cycle Time Percentile Report",
        start_date=datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc),  # Sunday
        end_date=datetime(2016, 7, 2, 11, 59, 59, tzinfo=tzutc),  # Saturday
        num_weeks=7,
    )
    report = r.report_on(weeks_of_tickets)

    assert len(report.table) == 8
    assert report.table == expected


def test_report_table_limit(klass, weeks_of_tickets, date, datetime, tzutc):
    """Ensure the report table returns no more than the num_weeks provided"""

    expected = [
        ["Week", "50th", "75th", "95th"],
        [date(2016, 6, 5), 14, 16, 17],
        [date(2016, 6, 12), 13, 16, 17],
        [date(2016, 6, 19), 10, 14, 18],
        [date(2016, 6, 26), 10, 15, 18],
    ]

    r = klass(
        title="Cycle Time Percentile Report",
        start_date=datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc),  # Sunday
        end_date=datetime(2016, 7, 2, 11, 59, 59, tzinfo=tzutc),  # Saturday
        num_weeks=4,
    )
    report = r.report_on(weeks_of_tickets)

    assert len(report.table) == 5
    assert report.table == expected


def test_report_table_no_tickets(klass, date, datetime, tzutc):
    """Ensure the report table returns a row for every week"""

    expected = [
        ["Week", "50th", "75th", "95th"],
        [date(2016, 5, 15), 0, 0, 0],
        [date(2016, 5, 22), 0, 0, 0],
        [date(2016, 5, 29), 0, 0, 0],
        [date(2016, 6, 5), 0, 0, 0],
        [date(2016, 6, 12), 0, 0, 0],
        [date(2016, 6, 19), 0, 0, 0],
        [date(2016, 6, 26), 0, 0, 0],
    ]

    r = klass(
        title="Cycle Time Percentile Report",
        start_date=datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc),  # Sunday
        end_date=datetime(2016, 7, 2, 11, 59, 59, tzinfo=tzutc),  # Saturday
        num_weeks=7,
    )
    report = r.report_on([])

    assert len(report.table) == 8
    assert report.table == expected
