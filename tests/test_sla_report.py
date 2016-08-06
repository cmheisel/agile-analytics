import pytest


@pytest.fixture
def klass():
    """Return the CUT."""
    from agile_analytics import SLAReporter
    return SLAReporter


def test_klass(klass):
    """Verify our fixture."""
    assert klass
