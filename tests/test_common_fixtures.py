"""Test common possibly complex fixtures."""


def test_weeks_of_tickets(weeks_of_tickets, datetime, tzutc):
    """Verify this rather complex fixture."""
    assert len(weeks_of_tickets) == 23
    assert weeks_of_tickets[0].ended['entered_at'] == datetime(2016, 5, 15, 0, 0, 0, tzinfo=tzutc)
    assert weeks_of_tickets[5].lead_time == 19
