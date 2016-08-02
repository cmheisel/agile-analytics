"""Shared fixtures."""
import pytest


@pytest.fixture
def days_agos(days_ago):
    """Return 45 dates ending with today."""
    days_agos = {}
    for i in range(0, 46):
        days_agos[i] = days_ago(i)
    return days_agos


@pytest.fixture
def AnalyzedAgileTicket():
    """Return a class used by the CUT."""
    from agile_analytics.models import AnalyzedAgileTicket
    return AnalyzedAgileTicket


@pytest.fixture
def datetime():
    """Return Datetime module."""
    from datetime import datetime
    return datetime


@pytest.fixture
def date():
    """Return Datetime module."""
    from datetime import date
    return date


@pytest.fixture
def tzutc():
    from dateutil.tz import tzutc
    return tzutc()


@pytest.fixture
def relativedelta():
    """Return relativedelta module."""
    from dateutil import relativedelta
    return relativedelta


@pytest.fixture
def StringIO():
    """Return StringIO."""
    import io
    return io


@pytest.fixture
def days_ago(datetime, relativedelta, tzutc):
    """Helper method for getting dates in the past."""
    def _days_ago(days):
        dt = datetime.now() - relativedelta.relativedelta(days=days)
        dt = dt.replace(second=0, microsecond=0, tzinfo=tzutc)
        return dt
    return _days_ago
