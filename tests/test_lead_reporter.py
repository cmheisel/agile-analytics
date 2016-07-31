"""Test Lead Time reporter."""

import pytest


@pytest.fixture
def klass():
    """Provide the CUT."""
    from agile_analytics import LeadTimeDistributionReporter
    return LeadTimeDistributionReporter


def test_klass(klass):
    """Ensure the fixture works."""
    assert klass
