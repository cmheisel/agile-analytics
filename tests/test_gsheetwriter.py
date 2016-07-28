import pytest


@pytest.fixture
def klass():
    """Return the CUT"""
    from agile_analytics import GSheetWriter
    return GSheetWriter


def test_klass(klass):
    """Ensure the fixture works."""
    assert klass


def test_get_credentials(klass, mocker):
    """Ensure we call the account credential reader correctly."""
    StubKlass = mocker.Mock(from_json_keyfile_name=mocker.Mock())

    k = klass('test_client_secret.json', StubKlass)

    StubKlass.from_json_keyfile_name.assert_called_once_with(
        "test_client_secret.json", k.scope
    )
