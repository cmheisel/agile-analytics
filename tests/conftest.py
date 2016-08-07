"""Shared fixtures."""
import csv
from os import path

import pytest


@pytest.fixture
def Ticket():
    """Create an AgileTicket for testing."""
    from agile_analytics.models import AgileTicket

    def _Ticket(**kwargs):
        flow_logs = kwargs.pop('flow_logs')
        key = kwargs.pop('key')
        t = AgileTicket(key=key, ttype="Story")
        for key, value in kwargs.items():
            setattr(t, key, value)
        for fl in flow_logs:
            t.flow_log.append(fl)
        return t
    return _Ticket


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


@pytest.fixture
def make_analyzed_tickets(AnalyzedAgileTicket, datetime, tzutc):
    """Make ticket from a list of dicts with key data."""
    from dateutil.parser import parse
    default = datetime(1979, 8, 15, 0, 0, 0, tzinfo=tzutc)

    def _make_analyzed_tickets(ticket_datas):
        tickets = []
        for data in ticket_datas:
            t = AnalyzedAgileTicket(
                key=data['key'],
                committed=dict(state="Committed", entered_at=parse(data['committed'], default=default)),
                started=dict(state="Started", entered_at=parse(data['started'], default=default)),
                ended=dict(state="Ended", entered_at=parse(data['ended'], default=default))
            )
            tickets.append(t)
        return tickets
    return _make_analyzed_tickets


@pytest.fixture
def weeks_of_tickets(datetime, tzutc, AnalyzedAgileTicket):
    """A bunch of tickets."""
    from dateutil.parser import parse
    parsed = []
    default = datetime(1979, 8, 15, 0, 0, 0, tzinfo=tzutc)

    current_path = path.dirname(path.abspath(__file__))
    csv_file = path.join(current_path, 'data', 'weeks_of_tickets.csv')

    count = 1
    for row in csv.DictReader(open(csv_file, 'r')):
        t = AnalyzedAgileTicket(
            key="FOO-{}".format(count),
            committed=dict(state="committed", entered_at=parse(row['committed'], default=default)),
            started=dict(state="started", entered_at=parse(row['started'], default=default)),
            ended=dict(state="ended", entered_at=parse(row['ended'], default=default))
        )
        parsed.append(t)
        count += 1

    return parsed
