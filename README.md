# jira-agile-extractor

[![Build Status](https://travis-ci.org/cmheisel/agile-analytics.svg?branch=master)](https://travis-ci.org/cmheisel/agile-analytics)
[![Coverage Status](https://coveralls.io/repos/github/cmheisel/agile-analytics/badge.svg?branch=master)](https://coveralls.io/github/cmheisel/agile-analytics?branch=master)
[![Stories in Ready](https://badge.waffle.io/cmheisel/agile-analytics.svg?label=ready&title=Ready)](http://waffle.io/cmheisel/agile-analytics)

Extract data about items from JIRA, output raw data and interesting reports

## Architecture

The agile extractor is composed of several different components. Fetchers gather data, which is fed to one or more analyzer/reporters/writer combos.

### Components

#### Fetchers

Fetchers are responsible for getting raw data about tickets from agile data sources (JIRA, Trello, etc.)

They depend on fetcher specific configuration including things like API end points, credentials and search criteria.

They produce a set of AgileTicket objects with a known interface.

#### Analyzers

Analyzers take in a set of AgileTicket objects and an analysis configuration and return a set of AnalyzedTicket objects that contain the original AgileTicket as well as additional data calculated in light of the analysis context.

For example, a CycleTime analyzer would look for a start_state and an end_state in the configuration, and calculate the days between those and store it as cycle_time on the AnalyzedTicket object.

#### Reporters

Reporters take in a set of AnalyzedTicket objects and a report configuration and return a Report object. It has two standard attributes:
* Table - A representation of the report as a 2 dimensional table, provides column headers, row labels, and values for each row/column combo
* Summary - A key/value store of report specific data

#### Writers

Writers take in a Report and a WriterConfig can write it out a particular source. Examples:
* CSV to standout
* CSV to a file
* Google spreadsheet
* Plotly

### Diagram

```
                                                            +----------->  Reporter: Distribution
                                                            |                title=Cycle Time Distribution
                                                            |                start_date=1/1/2015
                                                            |                end_date=3/31/2015
                                                            |                field=cycle_time
                                                            |
                                                            +----------->  Reporter: Throughput
                                                            |                title=Weekly Throughput
                                                            |                start_date=1/1/2015
                                                            |                end_date=3/31/2015
                                                            |                period=weekly
                                                            |
                                                            |
                                                            |
                 +----------------->  Analyzer: Cycle Time  +
                 |                      start_state=Backlog
                 |                      end_state=Deployed
                 |                      issue_types=Story
                 |
Fetcher          |                                          +-----------> Reporter: Throughput
  source=JIRA    +---------------->  Analyzer: Defect       +               title=Escaped Defects
  filter=1111    |                     defect_types=Bug,Incident            start_date=1/1/2015
  auth=user,pass |                                                          end_date=3/31/2015
                 |
                 |
                 +---------------->  Analyzer: Cycle Time   +-----------> Reporter: Throughput
                                       start_state=Analysis                 title=Weekly Analysis Throughput
                                       end_state=Dev                        start_date=1/1/2015
                                                                            end_date=3/31/2015
                                                                            period=weekly
```
