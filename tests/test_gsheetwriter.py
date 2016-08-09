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


def test_write_find_by_name(klass, mocker):
    """Ensure write finds docs by name."""
    report = mocker.Mock()
    report.table = [
        ['Ionic', 'Doric', 'Corinthian'],
        ['how to get the weeaboo to stop using the holodeck', 'malarkey', ''],
        ['does universal translator work on the weeaboo', ],
        ['can the brexit breed with the weeaboo', 'which moon is sailor moon from', 'is there dilithium in crystal pepsi'],
    ]

    starting_mock_cells = [
        MockCell("", 1, 1), MockCell("", 2, 1), MockCell("", 3, 1),
        MockCell("", 1, 2), MockCell("", 2, 2), MockCell("", 3, 2),
        MockCell("", 1, 3), MockCell("", 2, 3), MockCell("", 3, 3),
        MockCell("", 1, 4), MockCell("", 2, 4), MockCell("", 3, 4),
        MockCell("", 1, 5), MockCell("", 2, 5), MockCell("", 3, 5),
    ]

    mock_cell = MockCell("", 1, 1)
    mock_sheet_attrs = {
        'findall.return_value': [
            mock_cell,
        ],
        'range.return_value': starting_mock_cells
    }
    mock_sheet = mocker.Mock(**mock_sheet_attrs)
    mock_doc = mocker.Mock()
    mock_doc.worksheet.return_value = mock_sheet

    mock_driver_result = mocker.Mock()
    mock_driver_result.open.return_value = mock_doc
    klass.DRIVER_MODULE.authorize.return_value = mock_driver_result

    k = klass('foo')

    k.write(report, "Test Name", "Sheet Name")

    k.driver.open.called_once_with("Test Name")
    mock_doc.worksheet.called_once_with("Sheet Name")
    assert mock_cell.value == ""
    mock_sheet.range.assert_called_once_with('A1:C4')
    mock_sheet.update_cells.call_count == 2


def test_select_cells(klass, mocker):
    """Ensure the right cells are selcted."""
    report = mocker.Mock()
    report.table = [
        ['Ionic', 'Doric', 'Corinthian'],
        ['how to get the weeaboo to stop using the holodeck', 'malarkey', ''],
        ['does universal translator work on the weeaboo', ],
        ['can the brexit breed with the weeaboo', 'which moon is sailor moon from', 'is there dilithium in crystal pepsi'],
        ['', ]
    ]

    mock_sheet = mocker.Mock()

    k = klass('foo')
    k.select_range(mock_sheet, report.table)

    mock_sheet.range.assert_called_once_with('A1:C5')


class MockCell(object):
    def __init__(self, value, col, row):
        self.value = value
        self.col = col
        self.row = row

    def __repr__(self):
        return "<MockCell {}{}: '{}'>".format(self.col, self.row, self.value)


def test_update_cells(klass, mocker):
    """Ensure the cells are updated properly."""
    report = mocker.Mock()
    report.table = [
        ['Ionic', 'Doric', 'Corinthian'],
        ['how to get the weeaboo to stop using the holodeck', 'malarkey', ''],
        ['does universal translator work on the weeaboo', ],
        ['can the brexit breed with the weeaboo', 'which moon is sailor moon from', 'is there dilithium in crystal pepsi'],
        ['', ]
    ]
    starting_mock_cells = [
        MockCell("", 1, 1), MockCell("", 2, 1), MockCell("", 3, 1),
        MockCell("", 1, 2), MockCell("", 2, 2), MockCell("", 3, 2),
        MockCell("", 1, 3), MockCell("", 2, 3), MockCell("", 3, 3),
        MockCell("", 1, 4), MockCell("", 2, 4), MockCell("", 3, 4),
        MockCell("", 1, 5), MockCell("", 2, 5), MockCell("", 3, 5),
    ]
    expected_cells = [
        MockCell("Ionic", 1, 1), MockCell("Doric", 2, 1), MockCell("Corinthian", 3, 1),
        MockCell("how to get the weeaboo to stop using the holodeck", 1, 2), MockCell("malarkey", 2, 2), MockCell("", 3, 2),
        MockCell("does universal translator work on the weeaboo", 1, 3), MockCell("", 2, 3), MockCell("", 3, 3),
        MockCell("can the brexit breed with the weeaboo", 1, 4), MockCell("which moon is sailor moon from", 2, 4), MockCell("is there dilithium in crystal pepsi", 3, 4),
        MockCell("", 1, 5), MockCell("", 2, 5), MockCell("", 3, 5),
    ]

    k = klass('foo')
    actual = k.update_cells(starting_mock_cells, report.table)

    for actual_item, expected_item in zip(actual, expected_cells):
        assert (actual_item.row, actual_item.col, actual_item.value) == (expected_item.row, expected_item.col, expected_item.value)
