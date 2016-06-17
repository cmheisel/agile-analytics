"""Test the bundled analyzers."""

import pytest


@pytest.mark.fixture
def klass():
    """Return the Class Under Test."""
    from agile_analytics.analyzers import ThroughputAnalyzer
    return ThroughputAnalyzer
