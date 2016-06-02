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
