import csv


class CSVWriter(object):
    def write(self, destination, report):
        writer = csv.writer(destination)
        for row in report.table:
            writer.writerow(row)
