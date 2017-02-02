"""Tests the bundled fetchers and converters."""

from datetime import datetime

import pytest

from pretend import stub


@pytest.fixture
def tz():
    """Return a timezone."""
    from dateutil.tz import tzutc
    return tzutc()


@pytest.fixture
def klass():
    """Return the Class Under Test."""
    from agile_analytics.fetchers import JIRAFetcher
    return JIRAFetcher


@pytest.fixture
def converter():
    """Return the Function Under Test."""
    from agile_analytics.fetchers import convert_jira_issue
    return convert_jira_issue


@pytest.fixture
def jira_issue():
    """Mock jira issue.

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
        summary="This is my summary",
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


@pytest.fixture()
def JIRA(jira_issue):
    """Fake JIRA instance."""
    class MockJIRA(object):
        def __init__(self, *args, **kwargs):
            pass

        def search_issues(self, *args, **kwargs):
            return [jira_issue, ]
    return MockJIRA


def test_required_config(klass):
    """Test the required class instantiation values."""
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
    """Test what happens when the config is missing."""
    with pytest.raises(exc):
        klass(*args)


def test_weird_auth(klass):
    """Ensure we get a TypeError if the auth contains neither key."""
    auth = dict(random="bar", token_up="buuuuddddy")
    with pytest.raises(TypeError):
        klass(
            url="https://jira.example.local",
            auth=auth,
            filter_id=9999
        )


def test_basic_auth_kwargs(klass):
    """Ensure basic_auth kwargs are handeled."""
    basic_auth = dict(username="foo", password="bar")
    f = klass(
        url="https://jira.example.local",
        auth=basic_auth,
        filter_id=9999
    )
    expected = dict(basic_auth=("foo", "bar"))
    assert f.auth_kwargs == expected


def test_oauth_kwargs(klass):
    """Ensure oauth kwargs are handled."""
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
    """Ensure extra_kwargs work."""
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


def test_fetch(klass, JIRA):
    """Ensure the JIRAFetcher fetch method returns issues."""
    basic_auth = dict(username="foo", password="bar")
    f = klass(
        url="https://jira.example.local",
        auth=basic_auth,
        filter_id=9999,
    )
    tickets = f.fetch(jira_klass=JIRA)
    assert hasattr(tickets[0], 'flow_log')


def test_converter_key(jira_issue, converter):
    """Ensure a converted issue has a key."""
    t = converter(jira_issue)
    assert t.key == u"FOO-1"


def test_converter_summary(jira_issue, converter):
    """Ensure a convereted issue has a title."""
    t = converter(jira_issue)
    assert t.title == u"This is my summary"


def test_converter_summary_empty(jira_issue, converter):
    """Ensure a convereted issue has a title."""
    jira_issue.fields.summary = ''
    t = converter(jira_issue)
    assert t.title == u""


def test_converter_created_at(jira_issue, converter, tz):
    """Ensure created_at is populated."""
    t = converter(jira_issue)
    assert t.created_at == datetime(2016, 3, 30, 17, 27, 9, tzinfo=tz)


def test_converter_updated_at(jira_issue, converter, tz):
    """Ensure updated_at is populated."""
    t = converter(jira_issue)
    assert t.updated_at == datetime(2016, 5, 18, 16, 17, 21, tzinfo=tz)


def test_changelog_conversion(jira_issue, converter, tz):
    """Ensure the changelog is converted as expected."""
    expected = [
        dict(
            entered_at=datetime(2016, 3, 30, 17, 27, 9, tzinfo=tz),
            state=u"Created"
        ),
        dict(
            entered_at=datetime(2016, 4, 27, 14, 21, 23, tzinfo=tz),
            state=u"In Progress"
        ),
        dict(
            entered_at=datetime(2016, 4, 27, 14, 21, 24, tzinfo=tz),
            state=u"BLOCKED",
        ),
        dict(
            entered_at=datetime(2016, 5, 2, 14, 48, 32, tzinfo=tz),
            state=u"In Progress",
        ),
        dict(
            entered_at=datetime(2016, 5, 3, 18, 1, 10, tzinfo=tz),
            state=u"In QA",
        ),
        dict(
            entered_at=datetime(2016, 5, 5, 18, 42, 25, tzinfo=tz),
            state=u"Done",
        ),
        dict(
            entered_at=datetime(2016, 5, 18, 16, 17, 21, tzinfo=tz),
            state=u"Accepted",
        )
    ]

    i = jira_issue
    t = converter(i)

    assert t.flow_log == expected


def test_ticket_type_capture(jira_issue, converter, tz):
    """The type of ticket should be captured."""
    t = converter(jira_issue)
    assert t.type == "Story"


def test_ticket_type_default(jira_issue, converter, tz):
    """The type of ticket should be Ticket if issuetype can't be found."""
    del jira_issue.fields.issuetype
    t = converter(jira_issue)
    assert t.type == "Ticket"
