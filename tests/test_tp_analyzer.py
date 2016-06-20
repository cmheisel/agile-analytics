"""Test the bundled Cycle Date analyzer."""
from dateutil import relativedelta
from datetime import datetime

import pytest


@pytest.fixture
def klass():
    """Return the Class Under Test."""
    from agile_analytics.analyzers import DateAnalyzer
    return DateAnalyzer


@pytest.fixture
def analyzer(klass):
    """Return an instance of the CUT with some defaults."""
    a = klass(
        start_states=[u"In Progress", ],
        commit_states=[u"Selected", ],
        end_states=[u"Done", ]
    )
    return a


@pytest.fixture
def Ticket():
    """Create an AgileTicket for testing."""
    from agile_analytics.models import AgileTicket

    def _Ticket(**kwargs):
        flow_logs = kwargs.pop('flow_logs')
        key = kwargs.pop('key')
        t = AgileTicket(key=key)
        for key, value in kwargs.items():
            setattr(t, key, value)
        for fl in flow_logs:
            t.flow_log.append(fl)
        return t
    return _Ticket


@pytest.fixture
def days_ago():
    """Helper method for getting dates in the past."""
    def _days_ago(days):
        dt = datetime.now() - relativedelta.relativedelta(days=days)
        dt = dt.replace(second=0, microsecond=0)
        return dt
    return _days_ago


def test_config(analyzer):
    """Ensure the analyzer inits properly."""
    assert u"In Progress" in analyzer.start_states


def test_missing_config(klass):
    """Get an error."""
    with pytest.raises(TypeError):
        klass()


def test_analyze_no_data(analyzer):
    """Get an error."""
    with pytest.raises(TypeError):
        analyzer.analyze()


def test_analyze_entered_at(analyzer, Ticket, days_ago):
    """Analyzed tickets should have entered_at dates for all 3 states."""
    t = Ticket(
        key="TEST-1",
        created_at=days_ago(10),
        updated_at=days_ago(0),
        flow_logs=[
            dict(entered_at=days_ago(7), state="Selected"),
            dict(entered_at=days_ago(5), state="In Progress"),
            dict(entered_at=days_ago(2), state="Done")
        ]
    )
    results, ignored_issues = analyzer.analyze([t, ])
    assert results[0].ended['entered_at'] == days_ago(2)
    assert results[0].started['entered_at'] == days_ago(5)
    assert results[0].committed['entered_at'] == days_ago(7)
    assert len(ignored_issues) == 0


def test_analyze_missing_committed_state(analyzer, Ticket, days_ago):
    """A ticket which is missing committed, should be ignored."""
    t = Ticket(
        key="TEST-1",
        created_at=days_ago(10),
        updated_at=days_ago(0),
        flow_logs=[
            dict(entered_at=days_ago(7), state="Backlog"),  # Doesn't match config
            dict(entered_at=days_ago(5), state="In Progress"),
            dict(entered_at=days_ago(2), state="Done")
        ]
    )
    results, ignored_issues = analyzer.analyze([t, ])
    assert len(ignored_issues) == 1
