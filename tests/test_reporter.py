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
