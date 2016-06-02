import pytest

@pytest.fixture
def klass():
    from jira_agile_extractor.fetchers import JIRAFetcher
    return JIRAFetcher


def test_required_config(klass):
    f = klass(
        auth=dict(username="foo", password="bar"),
        filter_id=9999
    )
    assert f

@pytest.mark.parametrize("args,exc",[
    ((), TypeError),
    ((dict()), TypeError),
    ((dict(), None), TypeError),
])
def test_missing_config(klass, args, exc):
    with pytest.raises(exc):
        f = klass(*args)
