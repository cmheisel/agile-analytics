"""Make reports from data."""

from dateutil.relativedelta import relativedelta

class ThroughputReporter(object):
    """Generate throughput reports.

    Attributes:
        title (unicode): The name of the report
        period (unicode): The interval you'd like, one of daily, weekly, monthly,
        start_date (datetime): The starting range of the report.
        end_date (datetime): The ending range of the report.
    """

    def __init__(self, title, period=None, start_date=None, end_date=None):
        self.title = title
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        object.__init__(self)

    @property
    def start_date(self):
        return self.valid_start_date(self._start_date, self.period)

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self.valid_end_date(self._end_date, self.period)

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def valid_start_date(self, target_date, period):
        if period == "weekly" and target_date.weekday() != 6:
            # Walk back to a Sunday
            while target_date.weekday() != 6:
                target_date = target_date - relativedelta(days=1)

        return target_date

    def valid_end_date(self, target_date, period):
        if period == "weekly" and target_date.weekday() != 5:
            # Walk forward to a Saturday
            while target_date.weekday() != 5:
                target_date = target_date + relativedelta(days=1)

        return target_date
