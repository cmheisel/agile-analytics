"""Test the bundled analyzers."""

import pytest


@pytest.mark.fixture
def klass():
    """Return the Class Under Test."""
    from jira_agile_extractor.analyzers import ThroughputAnalyzer
    return ThroughputAnalyzer
