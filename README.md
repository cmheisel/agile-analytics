# jira-agile-extractor

[![Stories in Ready](https://badge.waffle.io/cmheisel/jira-agile-extractor.svg?label=ready&title=Ready)](http://waffle.io/cmheisel/jira-agile-extractor)

Extract data about items from JIRA, output raw data and interesting reports

## Architecture

The agile extractor is composed of several different components. Fetchers gather data, which is fed to one or more analyzer/reporters/writer combos.

### Components

#### Fetchers

Fetchers are responsible for get raw data about tickets from agile data sources.

They depend on fetcher specific configuration including things like API end points, credentials and search criteria.

They produce a set of AgileTicket objects with a known interface.

#### Analyzers

Analyzers take in a set of AgileTicket objects and a AnalysisConfig and return a set of AnalyzedTicket objects that contain the original AgileTicket as well as additional data calculated in light of the analysis context.

For example, a CycleTime analyzer would look for a start_date and an end_state in the AnalysisContext, and calculate the days between those and store it as cycle_time on the AnalyzedTicket object.

#### Reporters

Reporters take in a set of AnalyzedTicket objects a ReportConfig and return a Report object. It has two standard attributes:
* Table - A representation of the report as a 2 dimensional table, provides column headers, row labels, and values for each row/column combo
* Summary - A key/value store of report specific data

#### Writers

Writers take in a Report and a WriterConfig can write it out a particular source. Examples:
* CSV to standout
* CSV to a file
* GoogleSpreadsheet
* Plotly
