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
    def __init__(self, keyfile_name="client_secret.json"):
        self.keyfile_name = keyfile_name
        self.credentials = self.get_credentials()

    def get_credentials(self):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.keyfile_name, scope)
        return credentials

    def get_datasheet(self, doc, name="Data"):
        try:
            data_sheet = doc.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            data_sheet = doc.add_worksheet(name, 1, 1)
        return data_sheet

    def clear_sheet(self, sheet, rows, cols):
        sheet.resize(rows, cols)
        cell_list = sheet.findall(re.compile(".*", re.DOTALL))
        for cell in cell_list:
            cell.value = ""
        sheet.update_cells(cell_list)

    def append_to_sheet(self, sheet, data):
        row_count = 1
        for row in data:
            sheet.insert_row(row, index=row_count)
            row_count += 1

    def update_sheet(self, sheet, data):
        self.clear_sheet(sheet, 1, len(data[0]))
        self.append_to_sheet(sheet, data)

    def write(self, report, doc_id=None, doc_name=None, sheet_name="Data"):
        pass
