"""
test_fetchers
Tests the bundled fetchers and convers.
"""

from datetime import datetime

import pytest

from pretend import stub


@pytest.fixture
def tz():
    from dateutil.tz import tzutc
    return tzutc()


@pytest.fixture
def klass():
    from jira_agile_extractor.fetchers import JIRAFetcher
    return JIRAFetcher


@pytest.fixture
def converter():
    from jira_agile_extractor.fetchers import convert_jira_issue
    return convert_jira_issue


@pytest.fixture
def jira_issue():
    """
    Alternate way to get a JIRA issue mock
    ========================================
    from jira import JIRA
    from jira.resources import Issue

    #  Grab some fixtures
    j = JIRA(server=SERVER, basic_auth=(USERNAME, PASSWORD), options=dict(verify=False))
    i = j.issue("JIRATICKET-926", expand="changelog")
    json.dump(i, file("tests/json/jira_ticket.json", "w"), indent=True)  # Readable is better

    # Load said fixtures
    js = json.load(file("tests/json/jira_ticket.json", 'r'))
    i = Issue(options=None, session=None, raw=js)
    return i
    """

    fields = stub(
        issuetype=stub(
            name="Story"
        ),
        created="2016-03-30T17:27:09.000+0000",
        updated="2016-05-18T16:17:21.000+0000",
    )

    histories = [
        # history
        stub(
            created="2016-04-27T14:21:23.000+0000",
            items=[
                stub(field="status", fromString="Open", toString="In Progress"),
            ]
        ),
        stub(
            created="2016-04-27T14:21:24.000+0000",
            items=[
                stub(field="status", fromString="In Progress", toString="BLOCKED"),
            ]
        ),
        stub(
            created="2016-05-02T14:48:32.000+0000",
            items=[
                stub(field="status", fromString="BLOCKED", toString="In Progress"),
            ]
        ),
        stub(
            created="2016-05-03T18:01:10.000+0000",
            items=[
                stub(field="status", fromString="In Progress", toString="In QA"),
            ]
        ),
        stub(
            created="2016-05-05T18:42:25.000+0000",
            items=[
                stub(field="status", fromString="In QA", toString="Done"),
            ]
        ),
        stub(
            created="2016-05-18T16:17:21.000+0000",
            items=[
                stub(field="status", fromString="Done", toString="Accepted"),
            ]
        ),
    ]

    i = stub(
        key="FOO-1",
        fields=fields,
        changelog=stub(histories=histories)
    )
    return i


def test_required_config(klass):
    f = klass(
        url="https://jira.example.local",
        auth=dict(username="foo", password="bar"),
        filter_id=9999
    )
    assert f


@pytest.mark.parametrize("args,exc", [
    ((), TypeError),
    ((dict()), TypeError),
    ((dict(), None), TypeError),
])
def test_missing_config(klass, args, exc):
    with pytest.raises(exc):
        klass(*args)


def test_basic_auth_kwargs(klass):
    basic_auth = dict(username="foo", password="bar")
    f = klass(
        url="https://jira.example.local",
        auth=basic_auth,
        filter_id=9999
    )
    expected = dict(basic_auth=("foo", "bar"))
    assert f.auth_kwargs == expected


def test_oauth_kwargs(klass):
    oauth = dict(
        access_token="foo",
        access_token_secret="bar",
        consumer_key="baz",
        key_cert="---- BAT CERT ---"
    )
    f = klass(
        url="https://jira.example.local",
        auth=oauth,
        filter_id=9999
    )
    expected = dict(oauth=oauth)
    assert f.auth_kwargs == expected


def test_extra_kwargs(klass):
    basic_auth = dict(username="foo", password="bar")
    extra_kwargs = dict(options=dict(verify=False))
    f = klass(
        url="https://jira.example.local",
        auth=basic_auth,
        filter_id=9999,
        jira_kwargs=extra_kwargs
    )
    for key, value in extra_kwargs.items():
        assert f.jira_kwargs[key] == value


def test_converter_key(jira_issue, converter):
    t = converter(jira_issue)
    assert t.key == u"FOO-1"


def test_converter_created_at(jira_issue, converter, tz):
    t = converter(jira_issue)
    assert t.created_at == datetime(2016, 03, 30, 17, 27, 9, tzinfo=tz)


def test_converter_updated_at(jira_issue, converter, tz):
    t = converter(jira_issue)
    assert t.updated_at == datetime(2016, 05, 18, 16, 17, 21, tzinfo=tz)


def test_changelog_conversion(jira_issue, converter, tz):
    expected = [
        dict(
            entered_at=datetime(2016, 03, 30, 17, 27, 9, tzinfo=tz),
            state=u"Created"
        ),
        dict(
            entered_at=datetime(2016, 4, 27, 14, 21, 23, tzinfo=tz),
            state=u"In Progress"
        ),
        dict(
            entered_at=datetime(2016, 04, 27, 14, 21, 24, tzinfo=tz),
            state=u"BLOCKED",
        ),
        dict(
            entered_at=datetime(2016, 05, 02, 14, 48, 32, tzinfo=tz),
            state=u"In Progress",
        ),
        dict(
            entered_at=datetime(2016, 05, 03, 18, 01, 10, tzinfo=tz),
            state=u"In QA",
        ),
        dict(
            entered_at=datetime(2016, 05, 05, 18, 42, 25, tzinfo=tz),
            state=u"Done",
        ),
        dict(
            entered_at=datetime(2016, 05, 18, 16, 17, 21, tzinfo=tz),
            state=u"Accepted",
        )
    ]

    i = jira_issue
    t = converter(i)

    assert t.flow_log == expected
