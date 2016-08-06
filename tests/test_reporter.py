"""Test the Reporter base class."""

import pytest


@pytest.fixture
def klass():
    """Return the CUT."""
    from agile_analytics.reporters import Reporter
    return Reporter


def test_klass(klass):
    """Ensure the CUT exists."""
    assert klass


@pytest.fixture
def instance(klass, days_ago):
    """Return a pre-init'd CUT."""
    now = days_ago(0)
    a_month_ago = days_ago(30)

    k = klass(title="Foo", start_date=a_month_ago, end_date=now)
    return k


def test_init(klass, days_ago):
    """Verify we can init it correctly."""

    now = days_ago(0)
    a_month_ago = days_ago(30)

    k = klass(title="Foo", start_date=a_month_ago, end_date=now)

    assert k
    assert k.start_date == a_month_ago
    assert k.end_date == now


def test_valid_start_date(klass, days_ago):
    """Verify valid_start_date returns whatever is passed."""

    now = days_ago(0)
    a_month_ago = days_ago(30)

    k = klass(title="Foo", start_date=a_month_ago, end_date=now)

    assert now == k.valid_start_date(now)


def test_valid_end_date(klass, days_ago):
    """Verify valid_end_date returns whatever is passed."""
    now = days_ago(0)
    a_month_ago = days_ago(30)

    k = klass(title="Foo", start_date=a_month_ago, end_date=now)

    assert a_month_ago == k.valid_end_date(a_month_ago)


def test_filter_issues(instance):
    """Verify that filter_issues raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        instance.filter_issues([])


def test_report_on(instance):
    """Verify that report_on raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        instance.report_on([])


def test_starts_of_weeks(klass, relativedelta, datetime, tzutc):
    """Should return a list of datetimes == the Sundays starting each week between start_ and end_date."""
    instance = klass(
        title="Foo",
        start_date=datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc),  # Sunday,
        end_date=datetime(2016, 6, 25, 11, 59, 59, tzinfo=tzutc)  # Saturday
    )
    week_starts = list(instance.starts_of_weeks())
    expected_start_of_last_week = instance.end_date.date() - relativedelta.relativedelta(days=6)
    assert week_starts[0] == instance.start_date.date()
    assert week_starts[-1] == expected_start_of_last_week
    for start in week_starts:
        assert start.weekday() == instance.SUNDAY


def test_filter_on_ended(klass, days_agos, AnalyzedAgileTicket):
    """Verify that filter_on_ended only includes tickets that ended in the instance date range."""
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
    filtered_issues = r.filter_on_ended(issue_list)

    assert r.start_date > issue_out_of_range.ended['entered_at']
    assert len(filtered_issues) == 2
