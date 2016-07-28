import csv
import re

import gspread

from oauth2client.service_account import ServiceAccountCredentials


class CSVWriter(object):
    def write(self, destination, report):
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


# TODO: Needs tests and docstrings
class GSheetWriter(object):
    """Writes reports to Google Spreadsheets.
    Arguments:
        keyfile_name (str): The path to a JSON file with the service account credentials you want to use.
    """
    def __init__(self, keyfile_name="client_secret.json", credential_klass=ServiceAccountCredentials):
        self.keyfile_name = keyfile_name
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.credentials = self.get_credentials(self.keyfile_name, self.scope, credential_klass)

    def get_credentials(self, keyfile_name, scope, credential_klass):
        """Load the JSON and return ServiceAccountCredentials
        Arguments:
            keyfile_name (str): The path to the JSON containing the key file
            credential_klass (AssertionCredentials): A class that implements from_json_keyfile_name
        Returns:
            Credentials: The oauth2client compatible credentials object based on the JSON.
        """
        credentials = credential_klass.from_json_keyfile_name(keyfile_name, scope)
        return credentials

    def get_datasheet(self, doc, name="Data"):
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

    def append_to_sheet(self, sheet, data):
        """Appends the supplied data to the worksheet.
        Arguments:
            sheet (Worksheet): The worksheet you want the data appended to.
            data (array): The array of data you want appended to the sheet
        Returns:
            None
        """
        row_count = 1
        for row in data:
            sheet.insert_row(row, index=row_count)
            row_count += 1

    def update_sheet(self, sheet, data):
        """Clear a sheet and append the data to it.
        Arguments:
            sheet (Worksheet): The worksheet you want to modify
            data (array): The data you want the worksheet to contain
        Returns:
            None
        """
        self.clear_sheet(sheet, 1, len(data[0]))
        self.append_to_sheet(sheet, data)

    def write(self, report, doc_id=None, doc_name=None, sheet_name="Data"):
        pass
