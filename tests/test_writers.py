import pytest


@pytest.fixture
def klass():
    from agile_analytics import CSVWriter
    return CSVWriter


@pytest.fixture
def report(date):
    from collections import namedtuple
    Report = namedtuple("Report", ["summary", "table"])
    table = [
        ["Week", "Completed"],
        [date(2016, 5, 15), 4],
        [date(2016, 5, 22), 0],
        [date(2016, 5, 29), 0],
        [date(2016, 6, 5), 4],
        [date(2016, 6, 12), 0],
        [date(2016, 6, 19), 0],
    ]
    r = Report({}, table)
    return r


def test_init(klass):
    w = klass()
    assert w


def test_write(klass, report, StringIO):
    w = klass()
    csvstring = StringIO.StringIO()

    expected = r"""Week,Completed
2016-05-15,4
2016-05-22,0
2016-05-29,0
2016-06-05,4
2016-06-12,0
2016-06-19,0"""

    w.write(csvstring, report)
    expected = expected.split()
    actual = csvstring.getvalue().split()
    assert expected == actual
