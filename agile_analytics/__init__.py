"""Pulls data from agile systems and analyzes it."""

from .version import __version__, __author__

from .fetchers import (
    JIRAFetcher,
    convert_jira_issue
)

from .analyzers import (
    DateAnalyzer,
)

from .reporters import (
    ThroughputReporter,
    LeadTimeDistributionReporter,
)

from .writers import (
    CSVWriter,
    GSheetWriter
)

assert DateAnalyzer
assert JIRAFetcher
assert convert_jira_issue
assert CSVWriter
assert ThroughputReporter
assert LeadTimeDistributionReporter
assert GSheetWriter
assert __version__
assert __author__

version = ".".join(map(str, __version__))
