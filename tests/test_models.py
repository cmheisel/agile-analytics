import pytest


@pytest.fixture
def klass():
    from agile_analytics.models import AgileTicket
    return AgileTicket


@pytest.fixture
def datetime():
    from datetime import datetime
    return datetime


@pytest.fixture
def make_one(klass):
    def _make_one(*args, **kwargs):
        kwargs['key'] = kwargs.get('key', "TEST-1")
        return klass(*args, **kwargs)
    return _make_one


def test_construction(make_one):
    t = make_one()
    assert t


def test_flow_log_append_happy(make_one, datetime):
    t = make_one()
    t.flow_log.append(
        dict(
            entered_at=datetime.now(),
            state="Missouri"
        )
    )
    assert t.flow_log[0]


def test_flow_log_append_unicode(make_one, datetime):
    t = make_one()
    t.flow_log.append(
        dict(
            entered_at=datetime.now(),
            state="LA",
        )
    )
    assert t.flow_log[0][u'state'] == unicode("LA")


def test_flow_log_append_datetime(make_one, datetime):
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
    t = make_one()
    with pytest.raises(TypeError):
        t.flow_log.append(
            dict(
                state="SD",
                entered_at=str(datetime.now()),
            )
        )


def test_flow_log_append_unhappy_no_dict(make_one):
    t = make_one()
    with pytest.raises(TypeError):
        t.flow_log.append(['VT', '278461911'])
