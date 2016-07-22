"""Test the models."""

import pytest


@pytest.fixture
def klass():
    """Return CUT."""
    from agile_analytics.models import AgileTicket
    return AgileTicket


@pytest.fixture
def make_one(klass):
    """Function to make an AgileTicket."""
    def _make_one(*args, **kwargs):
        kwargs['key'] = kwargs.get('key', "TEST-1")
        return klass(*args, **kwargs)
    return _make_one


def test_construction(make_one):
    """Ensure make_one works."""
    t = make_one()
    assert t


def test_flow_log_append_happy(make_one, datetime):
    """Ensure FlowLogs require entered_at and state."""
    t = make_one()
    t.flow_log.append(
        dict(
            entered_at=datetime.now(),
            state="Missouri"
        )
    )
    assert t.flow_log[0]


def test_flow_log_append_unicode(make_one, datetime):
    """Ensure flow log strings are unicode."""
    t = make_one()
    t.flow_log.append(
        dict(
            entered_at=datetime.now(),
            state="LA",
        )
    )
    assert t.flow_log[0][u'state'] == unicode("LA")


def test_flow_log_append_datetime(make_one, datetime):
    """Ensure flow log datetimes are honored."""
    test_dt = datetime.now()
    t = make_one()
    t.flow_log.append(
        dict(
            entered_at=test_dt,
            state="OK"
        )
    )
    assert t.flow_log[0][u'entered_at'] == test_dt


def test_flow_log_append_unhappy(make_one, datetime):
    """Ensure we only accept datetime-ish objects."""
    t = make_one()
    with pytest.raises(TypeError):
        t.flow_log.append(
            dict(
                state="SD",
                entered_at=str(datetime.now()),
            )
        )


def test_flow_log_append_unhappy_no_dict(make_one):
    """Ensure we only accept dict-ish objects."""
    t = make_one()
    with pytest.raises(TypeError):
        t.flow_log.append(['VT', '278461911'])


def test_flow_log_ordered_ascending(make_one, days_ago):
    """Ensure flow log items are oldest > newest."""
    t = make_one()
    items = [
        dict(state="SC", entered_at=days_ago(2)),
        dict(state="KNAP", entered_at=days_ago(8)),
        dict(state="Junohaki", entered_at=days_ago(9)),
        dict(state="MA", entered_at=days_ago(10))
    ]
    for i in items:
        t.flow_log.append(i)

    actual = [fl['state'] for fl in t.flow_log]
    expected = [
        "MA",
        "Junohaki",
        "KNAP",
        "SC"
    ]
    assert actual == expected
