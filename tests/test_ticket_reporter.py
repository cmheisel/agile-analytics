"""Test the TicketReporter class."""

import pytest


@pytest.fixture
def klass():
    from agile_analytics import TicketReporter
    return TicketReporter


def test_klass(klass):
    assert klass
