"""Shared fixtures."""
import pytest


@pytest.fixture
def datetime():
    """Return Datetime module."""
    from datetime import datetime
    return datetime


@pytest.fixture
def relativedelta():
    """Return relativedelta module."""
    from dateutil import relativedelta
    return relativedelta


@pytest.fixture
def days_ago(datetime, relativedelta):
    """Helper method for getting dates in the past."""
    def _days_ago(days):
        dt = datetime.now() - relativedelta.relativedelta(days=days)
        dt = dt.replace(second=0, microsecond=0)
        return dt
    return _days_ago