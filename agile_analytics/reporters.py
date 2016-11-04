"""Make reports from data."""

from collections import namedtuple
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc

from numpy import histogram, array, arange, percentile, round

Report = namedtuple("Report", ["table", "summary"])


class Reporter(object):
    """Base class for Reporters.

    Attributes:
        title (unicode): The name of the report
        start_date (datetime): The starting range of the report.
        end_date (datetime): The ending range of the report.
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __init__(self, title, start_date=None, end_date=None):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        super().__init__()

    @property
    def start_date(self):
        return self.valid_start_date(self._start_date)

    @start_date.setter
    def start_date(self, value):
        if value and value.tzinfo is None:
            value = value.replace(tzinfo=tzutc())
        self._start_date = value

    @property
    def end_date(self):
        return self.valid_end_date(self._end_date)

    @end_date.setter
    def end_date(self, value):
        if value and value.tzinfo is None:
            value = value.replace(tzinfo=tzutc())
        self._end_date = value

    def valid_start_date(self, target_date):
        """Returns a date that is valid for the start of the report.
        Arguments:
            target_date (datetime): The date you'd like examined
        Returns:
            datetime: A datetime made valid for the report based on the target_date argument.
        """
        return target_date

    def valid_end_date(self, target_date):
        """Returns a date that is valid for the end of the report.
        Arguments:
            target_date (datetime): The date you'd like examined
        Returns:
            datetime: A datetime made valid for the report based on the target_date argument.
        """
        return target_date

    def walk_back_to_weekday(self, target_date, day):
        """Returns the nearest date that predates the target_date.
        Arguments:
            target_date (datetime): The date to start with.
            day (int): An integer between 0 (Monday) and 6 (Sunday)
        Returns:
            datetime: The nearest date that predates the target_date for the given day.
        """
        while target_date.weekday() != day:
            target_date = target_date - relativedelta(days=1)
        return target_date

    def walk_forward_to_weekday(self, target_date, day):
        """Returns the nearest date that postdates the target_date.
        Arguments:
            target_date (datetime): The date to start with.
            day (int): An integer between 0 (Monday) and 6 (Sunday)
        Returns:
            datetime: The nearest date that postdates the target_date for the given day.
        """
        while target_date.weekday() != day:
            target_date = target_date + relativedelta(days=1)
        return target_date

    def filter_on_ended(self, issues):
        """Returns issues that were ended between the instances start/end dates.
        Arguments:
            issues (list[AnalyzedAgileTicket]): List of issues to be filtered_issues
        Return:
            list[AnalyzedAgileTicket]: List of issues that match.
        """
        filtered_issues = [i for i in issues if i.ended and (i.ended['entered_at'] >= self.start_date and i.ended['entered_at'] <= self.end_date)]
        return filtered_issues

    def filter_on_committed(self, issues):
        """Returns issues that were committed to between the instances start/end dates.
        Arguments:
            issues (list[AnalyzedAgileTicket]): List of issues to be filtered_issues
        Return:
            list[AnalyzedAgileTicket]: List of issues that match.
        """
        filtered_issues = [i for i in issues if i.ended and (i.committed['entered_at'] >= self.start_date and i.committed['entered_at'] <= self.end_date)]
        return filtered_issues

    def starts_of_weeks(self):
        """Return a list of dates that start each week between start_date and end_date."""
        week_starting = self.walk_back_to_weekday(self.start_date.date(), self.SUNDAY)
        while week_starting <= self.end_date.date():
            yield week_starting
            week_starting += relativedelta(days=7)

    def filter_issues(self, issues):
        raise NotImplementedError

    def report_on(self, issues, header=True):
        raise NotImplementedError


class CreatedReporter(Reporter):
    """Generates a report listing counts for all the types of tickets created each week."""
    def valid_start_date(self, target_date):
        """Ensure we start on a Sunday."""
        target_date = super().valid_start_date(target_date)
        return self.walk_back_to_weekday(target_date, self.SUNDAY)

    def valid_end_date(self, target_date):
        """Ensure we end on a Sunday."""
        target_date = super().valid_end_date(target_date)
        return self.walk_forward_to_weekday(target_date, self.SATURDAY)

    def filter_issues(self, issues):
        """Ignore issues completed outside the start/end range."""
        return self.filter_on_committed(issues)

    def _issues_for_week(self, week_start, issues):
        week_end = self.walk_forward_to_weekday(week_start, self.SATURDAY)
        week_start = datetime(week_start.year, week_start.month, week_start.day, 0, 0, 0, tzinfo=tzutc())
        week_end = datetime(week_end.year, week_end.month, week_end.day, 11, 59, 59, tzinfo=tzutc())
        return [i for i in issues if i.committed['entered_at'] >= week_start and i.committed['entered_at'] <= week_end]

    def report_on(self, issues, header=True):
        """Generate a report, one row per week, with counts for each ticket type."""
        issues = self.filter_issues(issues)
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                start_date=self.start_date,
                end_date=self.end_date
            )
        )

        ticket_types = list(set([issue.type for issue in issues]))
        ticket_types.sort()
        headers = ["Week", ]
        headers.extend(ticket_types)
        r.table.append(headers)

        for sunday in self.starts_of_weeks():
            this_weeks_issues = self._issues_for_week(sunday, issues)
            row = [sunday, ]
            for ttype in ticket_types:
                row.append(len([i for i in this_weeks_issues if i.type == ttype]))
            r.table.append(row)

        return r


class TicketReporter(Reporter):
    """Generates a report listing all the tickets that match the filter critiera."""
    def valid_start_date(self, target_date):
        """Ensure we start on a Sunday."""
        target_date = super().valid_start_date(target_date)
        return self.walk_back_to_weekday(target_date, self.SUNDAY)

    def valid_end_date(self, target_date):
        """Ensure we end on a Sunday."""
        target_date = super().valid_end_date(target_date)
        return self.walk_forward_to_weekday(target_date, self.SATURDAY)

    def filter_issues(self, issues):
        """Ignore issues completed outside the start/end range."""
        return self.filter_on_ended(issues)

    def report_on(self, issues, header=True):
        """Generate a report, one row per issue, with details."""
        issues = self.filter_issues(issues)
        issues.sort(key=lambda x: x.ended['entered_at'])
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                start_date=self.start_date,
                end_date=self.end_date
            )
        )

        r.table.append(
            ["Key", "Lead Time", "Commit State", "Commit At", "Start State", "Start At", "End State", "End At"],
        )
        for i in issues:
            row = [
                i.key,
                i.lead_time,
                i.committed['state'],
                i.committed['entered_at'],
                i.started['state'],
                i.started['entered_at'],
                i.ended['state'],
                i.ended['entered_at'],
            ]
            r.table.append(row)

        return r


class SLAReporter(Reporter):
    """Generates a report showing the number of tickets per week that exceeded their SLA."""
    def valid_start_date(self, target_date):
        """Ensure we start on a Sunday."""
        target_date = super().valid_start_date(target_date)
        return self.walk_back_to_weekday(target_date, self.SUNDAY)

    def valid_end_date(self, target_date):
        """Ensure we end on a Sunday."""
        target_date = super().valid_end_date(target_date)
        return self.walk_forward_to_weekday(target_date, self.SATURDAY)

    def filter_issues(self, issues):
        """Ignore issues completed outside the start/end range."""
        return self.filter_on_ended(issues)

    def _issues_for_week(self, week_start, issues):
        week_end = self.walk_forward_to_weekday(week_start, self.SATURDAY)
        week_start = datetime(week_start.year, week_start.month, week_start.day, 0, 0, 0, tzinfo=tzutc())
        week_end = datetime(week_end.year, week_end.month, week_end.day, 11, 59, 59, tzinfo=tzutc())
        return [i for i in issues if i.ended['entered_at'] >= week_start and i.ended['entered_at'] <= week_end]

    def report_on(self, issues, sla_config={}, header=True):
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                start_date=self.start_date,
                end_date=self.end_date
            )
        )

        issues = self.filter_issues(issues)
        ticket_types = list(set([issue.type for issue in issues]))
        ticket_types.sort()
        headers = ["Week", ]
        headers.extend(ticket_types)
        r.table.append(headers)

        for sunday in self.starts_of_weeks():
            this_weeks_issues = self._issues_for_week(sunday, issues)
            row = [sunday, ]
            for ttype in ticket_types:
                row.append(len([i for i in this_weeks_issues if i.type == ttype and i.lead_time > sla_config[ttype]]))
            r.table.append(row)

        return r


class LeadTimeDistributionReporter(Reporter):
    """Generates lead time distribution report for tickets completed in a single date range."""

    def valid_start_date(self, target_date):
        """Ensure we start on a Sunday."""
        target_date = super().valid_start_date(target_date)
        return self.walk_back_to_weekday(target_date, self.SUNDAY)

    def valid_end_date(self, target_date):
        """Ensure we end on a Sunday."""
        target_date = super().valid_end_date(target_date)
        return self.walk_forward_to_weekday(target_date, self.SATURDAY)

    def filter_issues(self, issues):
        """Ignore issues completed outside the start/end range."""
        return self.filter_on_ended(issues)

    def report_on(self, issues, header=True):
        """Generate a report object with a lead time histogram."""
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                start_date=self.start_date,
                end_date=self.end_date
            )
        )
        r.table.append(["Lead Time", "Tickets"])
        filtered_issues = self.filter_issues(issues)

        if filtered_issues:
            lead_times = [i.lead_time for i in filtered_issues]
            lead_times = array(lead_times)
            hist_values, hist_bins = histogram(
                lead_times,
                bins=arange(0, max(lead_times) + 2, 1)
            )

            for i in range(0, len(hist_values)):
                if i == 0:
                    continue
                row = [hist_bins[i], hist_values[i]]
                r.table.append(row)
        return r


class TimePercentileReporter(Reporter):
    """Report on Time Percentiles, calculated over a configurable (default 4) week period.
    Attributes:
        title (unicode): The name of the report
        start_date (datetime): The starting range of issues for the report.
        end_date (datetime): The ending range of issues for the report.
        num_weeks (int): The number of weeks you'd like reported on. Default: 4
    """

    def __init__(self, title, time_attr, start_date=None, end_date=None, num_weeks=4):
        super().__init__(title, start_date, end_date)
        self.num_weeks = num_weeks
        self.time_attr = time_attr

    def valid_start_date(self, target_date):
        target_date = super().valid_start_date(target_date)
        target_date = self.walk_back_to_weekday(target_date, self.SUNDAY)
        return target_date

    def valid_end_date(self, target_date):
        target_date = super().valid_end_date(target_date)
        target_date = self.walk_forward_to_weekday(target_date, self.SATURDAY)
        return target_date

    def filter_issues(self, issues):
        return self.filter_on_ended(issues)

    def _times_for_week(self, week_start, issues):
        week_end = self.walk_forward_to_weekday(week_start, self.SATURDAY)
        week_start = datetime(week_start.year, week_start.month, week_start.day, 0, 0, 0, tzinfo=tzutc())
        week_end = datetime(week_end.year, week_end.month, week_end.day, 11, 59, 59, tzinfo=tzutc())
        return [getattr(i, self.time_attr) for i in issues if i.ended['entered_at'] >= week_start and i.ended['entered_at'] <= week_end]

    def report_on(self, issues, header=True):
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                start_date=self.start_date,
                end_date=self.end_date,
                num_weeks=self.num_weeks)
        )
        if header:
            headers = ["Week", "50th", "75th", "95th"]
            r.table.append(headers)

        issues = self.filter_issues(issues)

        percentiles_by_week = []
        moving_sample = []
        for sunday in self.starts_of_weeks():
            moving_sample.append(self._times_for_week(sunday, issues))
            # Lets limit our percentile calc to the past 4 weeks
            if len(moving_sample) > 4:
                moving_sample.pop(0)

            samples = []
            for sample_set in moving_sample:
                samples.extend(sample_set)

            try:
                the_50th = int(round(percentile(samples, 50)))
                the_75th = int(round(percentile(samples, 75)))
                the_95th = int(round(percentile(samples, 95)))
            except IndexError:
                the_50th, the_75th, the_95th = 0, 0, 0

            percentiles_by_week.append([sunday, the_50th, the_75th, the_95th])

        for row in percentiles_by_week[-self.num_weeks:]:
            r.table.append(row)

        return r


class LeadTimePercentileReporter(TimePercentileReporter):
    def __init__(self, title, start_date=None, end_date=None, num_weeks=4):
        super(LeadTimePercentileReporter, self).__init__(title, "lead_time", start_date=start_date, end_date=end_date, num_weeks=num_weeks)


class CycleTimePercentileReporter(TimePercentileReporter):
    def __init__(self, title, start_date=None, end_date=None, num_weeks=4):
        super(CycleTimePercentileReporter, self).__init__(title, "cycle_time", start_date=start_date, end_date=end_date, num_weeks=num_weeks)


class ThroughputReporter(Reporter):
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
        super().__init__(title, start_date, end_date)

    def valid_start_date(self, target_date):
        target_date = super().valid_start_date(target_date)
        if self.period == "weekly":
            target_date = self.walk_back_to_weekday(target_date, self.SUNDAY)
        return target_date

    def valid_end_date(self, target_date):
        target_date = super().valid_end_date(target_date)
        if self.period == "weekly":
            target_date = self.walk_forward_to_weekday(target_date, self.SATURDAY)
        return target_date

    def _count_by_week(self, issues):
        counted_by_week = {}
        for week_starting in self.starts_of_weeks():
            week_end = week_starting + relativedelta(days=6)
            counted_by_week[week_starting] = len(
                [i for i in issues if i.ended['entered_at'].date() >= week_starting and i.ended['entered_at'].date() <= week_end]
            )

        return counted_by_week

    def filter_issues(self, issues):
        return self.filter_on_ended(issues)

    def report_on(self, issues, header=True):
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                period=self.period,
                start_date=self.start_date,
                end_date=self.end_date
            )
        )
        r.table.append(["Week", "Completed"])
        filtered_issues = self.filter_issues(issues)
        counted_by_week = self._count_by_week(filtered_issues)

        weeks = list(counted_by_week.keys())
        weeks.sort()
        for week in weeks:
            r.table.append([week, counted_by_week[week]])

        return r
