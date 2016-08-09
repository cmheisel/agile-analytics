import csv
import re

import gspread

from oauth2client.service_account import ServiceAccountCredentials


class CSVWriter(object):
    def write(self, report, destination):
        """Write a CSV version of the report.
        Arguments:
            desitnation (file-like object): The file-like object where the data should be written to.
            report (Report): The Report instance that should be written to the destination.
        Returns:
            None
        """
        writer = csv.writer(destination)
        for row in report.table:
            writer.writerow(row)


class GSheetWriter(object):
    """Writes reports to Google Spreadsheets.
    Arguments:
        keyfile_name (str): The path to a JSON file with the service account credentials you want to use.
    """

    CREDENTIAL_CLASS = ServiceAccountCredentials
    DRIVER_MODULE = gspread
    COLUMN_OPTIONS = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split(' ')

    def __init__(self, keyfile_name="client_secret.json"):
        self.keyfile_name = keyfile_name
        self.scope = ['https://spreadsheets.google.com/feeds']

    @property
    def credentials(self):
        """Load the JSON and return ServiceAccountCredentials
        Returns:
            Credentials: The oauth2client compatible credentials object based on the JSON.
        """
        credentials = self.CREDENTIAL_CLASS.from_json_keyfile_name(self.keyfile_name, self.scope)
        return credentials

    @property
    def driver(self):
        return self.DRIVER_MODULE.authorize(self.credentials)

    def get_datasheet(self, doc, name):
        """Finds (or creates) the worksheet in the supplied google spreadsheet.
        Arguments:
            doc (Spreadsheet): The spreadsheet instance where you'd like the worksheet to exist.
            name (str default="Data"): The name of the worksheet you'd like to exist.
        Returns:
            Worksheet: The worksheet requested.
        """
        try:
            data_sheet = doc.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            data_sheet = doc.add_worksheet(name, 1, 1)
        return data_sheet

    def clear_sheet(self, sheet, rows, cols):
        """Deletes all data on the supplied sheet by resizing it.
        Arguments:
            sheet (Worksheet): The worksheet you want cleared.
            rows (int): The number of rows the cleared out sheet should end up with.
            cols (int): The number of rows the cleared out sheet should end up with.
        Returns:
            None
        """
        sheet.resize(rows, cols)
        cell_list = sheet.findall(re.compile(".*", re.DOTALL))
        for cell in cell_list:
            cell.value = ""
        sheet.update_cells(cell_list)

    def select_range(self, sheet, data):
        """Returns the cells that will be modified to match the new data.
        Arguments:
            sheet (Worksheet): The worksheet you want to put data into.
            data (array): The array of data you want placed into the sheet.
        Returns:
            list[Cell]: The list of gspread.Cells that should be replaced to match the data.
        """
        start_cell = "A1"  # Always and forever
        end_cell = "{}{}".format(
            self.COLUMN_OPTIONS[len(data[0]) - 1],
            len(data)
        )
        return sheet.range("{}:{}".format(start_cell, end_cell))

    def update_cells(self, cells, data):
        """Updates the cells, in batch, with the data provided.
        Arguments:
            cells (list[Cell]): The list of gspread.Cells that should be replaced to match the data.
            data (array): The array of data you want placed into the sheet.
        Returns:
            None
        """
        for i in range(0, len(cells)):
            cell = cells[i]
            row, col = cell.row, cell.col
            row_index = row - 1
            col_index = col - 1
            try:
                value = data[row_index][col_index]
                cell.value = value
            except IndexError:  # Leave as is, not in data
                pass

        return cells

    def batch_update_sheet(self, sheet, data):
        """Clear a sheet and append the data to it.
        Arguments:
            sheet (Worksheet): The worksheet you want to modify
            data (array): The data you want the worksheet to contain
        Returns:
            None
        """
        self.clear_sheet(sheet, len(data), len(data[0]))
        cells = self.select_range(sheet, data)
        cells = self.update_cells(cells, data)
        sheet.update_cells(cells)

    def write(self, report, doc_name, sheet_name):
        doc = self.driver.open(doc_name)
        sheet = self.get_datasheet(doc, sheet_name)
        self.batch_update_sheet(sheet, report.table)
