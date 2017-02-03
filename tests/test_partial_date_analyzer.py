import pytest


@pytest.fixture
def klass():
    """Return the CUT."""
    from agile_analytics import PartialDateAnalyzer
    return PartialDateAnalyzer


@pytest.fixture
def analyzer(klass):
    """Return an instance of the CUT with some defaults."""
    a = klass(
        start_states=["In Progress", ],
        commit_states=["Selected", "Created"],
        end_states=["Done", ]
    )
    return a


def test_created_ticket(Ticket, klass, days_ago, analyzer):
    """Tickets that been created, but not started/finished, should be handled."""
    t = Ticket(
        key="TEST-1",
        created_at=days_ago(10),
        updated_at=days_ago(0),
        flow_logs=[
            dict(entered_at=days_ago(10), state="Created"),
        ]
    )
    results, ignored_issues = analyzer.analyze([t, ])
    assert results[0].committed['entered_at'] == days_ago(10)
    assert len(ignored_issues) == 0


def test_created_ticket_title(Ticket, klass, days_ago, analyzer):
    """Tickets title should be propogated"""
    t = Ticket(
        key="TEST-1",
        title="Foo",
        created_at=days_ago(10),
        updated_at=days_ago(0),
        flow_logs=[
            dict(entered_at=days_ago(10), state="Created"),
        ]
    )
    results, ignored_issues = analyzer.analyze([t, ])
    assert results[0].title == "Foo"
