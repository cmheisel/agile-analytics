import pytest


@pytest.fixture
def klass():
    from jira_agile_extractor.fetchers import JIRAFetcher
    return JIRAFetcher


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
