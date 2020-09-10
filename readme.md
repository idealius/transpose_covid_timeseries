# Sanitize COVID-19 Data

Downloads time series data for deaths and confirmed cases from John Hopkins COVID-19's github
Then, sanitizes it so it is workable in common visualization software (Excel, Tableau, QGIS, etc.) and writes to a file with absolute values and per capita values **in percent** (multiplied by 100.)

Requirements: Windows 10 (Maybe Windows 8/7 would work)

### Instructions


1. Install Python 3.x
(https://www.python.org/downloads/)

2. Install wget, add to PATH, then run `downloadcovid.bat`
- OR-
Right-click `downloadcovid.ps1` then click Run with Powershell

3. From command line e.g. run

`python sanitize_covid_data_cases.py`

or

`sanitize_covid_data_cases`

or for running all of them:

`sanitize_covid\sanitize_data`

4. Files saved with their original filenames with '_t' suffix

### Features:

- Transposes dates so each row has a date, country, and case/death data both absolute and per capita
- Creates `us_cause_of_death_2015_t.csv` from CDC 2015 data listing the top 5 causes of death per state absolute and per capita
- Adds lockdown and tracing data to global output files (must be manually updated from `https://ourworldindata.org/grapher/covid-contact-tracing`
- All output files should be easily joined with other tables including `population_table.csv`

### Major Bugs:
9/10/2020: Per capita for confirmed cases in US doesn't have population column so it shows -1, probably causes some date data corruption as well

### Superficial Bugs:
Bonaire and surround islands incorrectly interpreted.
Congo incorrectly interpreted.

Read sources.txt for direct links to different data sources
Thank you