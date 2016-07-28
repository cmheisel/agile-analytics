"""Test the GSheetWriter."""

import pytest


@pytest.fixture
def gspread():
    import gspread
    return gspread


@pytest.fixture
def orig_class():
    """Return the CUT with network access enabled"""
    from agile_analytics import GSheetWriter
    return GSheetWriter


def test_orig_class(orig_class):
    """Ensure the fixture works."""
    assert orig_class.__name__ == "GSheetWriter"


@pytest.fixture
def klass(orig_class, mocker):
    """Return the CUT with some networky bits mocked out."""
    credential_mock_attrs = {
        'from_json_keyfile_name.return_value': "FakeTestCredentials"
    }
    driver_mock_attrs = {
    }
    orig_class.CREDENTIAL_CLASS = mocker.Mock(**credential_mock_attrs)
    orig_class.DRIVER_MODULE = mocker.Mock(**driver_mock_attrs)
    return orig_class


def test_klass_init(klass):
    """Ensure the CUT can be initialized."""
    k = klass('test_secret.json')
    assert k.keyfile_name == 'test_secret.json'


def test_driver(klass):
    """Ensure the driver is initialized properly."""
    k = klass('test_secret.json')

    assert k.driver

    k.CREDENTIAL_CLASS.from_json_keyfile_name.assert_called_once_with(
        'test_secret.json',
        k.scope
    )

    k.DRIVER_MODULE.authorize.assert_called_once_with('FakeTestCredentials')


def test_get_datasheet_happy(klass, mocker):
    """Ensure the get_datasheet method finds existing sheets."""
    k = klass('foo')

    mock_doc = mocker.Mock()
    k.get_datasheet(mock_doc, "Foo")
    mock_doc.worksheet.called_once_with("Foo")
    mock_doc.add_worksheet.assert_not_called()


def test_get_datasheet_exception(klass, mocker, gspread):
    """Ensure get datasheet method creates one if the requested name doesn't exist."""
    k = klass('foo')

    mock_doc_attrs = {
        'worksheet.side_effect': gspread.exceptions.WorksheetNotFound
    }
    mock_doc = mocker.Mock(**mock_doc_attrs)
    k.get_datasheet(mock_doc, "Foo")
    mock_doc.worksheet.called_once_with("Foo")
    mock_doc.add_worksheet.called_once_with("Foo", 1, 1)


def test_clear_sheet_resizes(klass, mocker):
    """Verify clear_sheet resizes."""
    mock_attrs = {
        'findall.return_value': []
    }
    mock_sheet = mocker.Mock(**mock_attrs)

    k = klass('foo')
    k.clear_sheet(mock_sheet, 1, 20)
    mock_sheet.resize.assert_called_once_with(1, 20)


def test_clear_sheet_replaces_content(klass, mocker):
    """Verify clear_sheet empties out any remaining content."""
    mock_cell = mocker.Mock(value="Hanging Chad")
    mock_sheet_attrs = {
        'findall.return_value': [
            mock_cell
        ]
    }
    mock_sheet = mocker.Mock(**mock_sheet_attrs)

    k = klass('foo')
    k.clear_sheet(mock_sheet, 1, 1)

    assert mock_cell.value == ""
    mock_sheet.update_cells.assert_called_once_with([mock_cell, ])


def test_append_to_sheet(klass, mocker):
    """Verify append_to_sheet appends only the data passed to it."""

    fistful_of_datas = [
        ['Ionic', 'Doric', 'Corinthian'],
        ['how to get the weeaboo to stop using the holodeck', 'malarkey', ''],
        ['does universal translator work on the weeaboo', ],
        ['can the brexit breed with the weeaboo', 'which moon is sailor moon from', 'is there dilithium in crystal pepsi'],
    ]

    mock_sheet = mocker.Mock()

    k = klass('foo')
    k.append_to_sheet(mock_sheet, fistful_of_datas)

    assert mock_sheet.insert_row.call_count == len(fistful_of_datas)


def test_update_sheet(klass, mocker):
    """Ensure update_sheet clears the data and then adds the new data."""
    fistful_of_datas = [
        ['Ionic', 'Doric', 'Corinthian'],
        ['how to get the weeaboo to stop using the holodeck', 'malarkey', ''],
        ['does universal translator work on the weeaboo', ],
        ['can the brexit breed with the weeaboo', 'which moon is sailor moon from', 'is there dilithium in crystal pepsi'],
    ]

    mock_cell = mocker.Mock(value="Hanging Chad")
    mock_sheet_attrs = {
        'findall.return_value': [
            mock_cell
        ]
    }
    mock_sheet = mocker.Mock(**mock_sheet_attrs)

    k = klass('foo')
    k.update_sheet(mock_sheet, fistful_of_datas)

    mock_sheet.resize.assert_called_once_with(1, 3)
    assert mock_cell.value == ""
    mock_sheet.update_cells.assert_called_once_with([mock_cell, ])
    assert mock_sheet.insert_row.call_count == len(fistful_of_datas)
