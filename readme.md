# Sanitize COVID-19 Data

Downloads time series data for deaths and confirmed cases from John Hopkins COVID-19's github
Then, sanitizes and transposes it so it is workable in common visualization software (Excel, Tableau, QGIS, etc.) for a timelapse and writes to a file with absolute values and per capita values **in percent (multiplied by 100.)**

Requirements: Windows 10 (Maybe Windows 8/7 would work)

### Instructions


1. Install Python 3.x
(https://www.python.org/downloads/)

2. Install pdfminer3. From command line:

`pip3 install pdfminer3`

3. Install wget, add to PATH, then run `downloadcovid.bat`
- OR-
Right-click `downloadcovid.ps1` then click Run with Powershell

4. From command line run:

`python sanitize_covid_data_cases.py`

or

`sanitize_covid_data_cases.py`

or for running all of them:

`sanitize_covid\sanitize_data`

5. Files saved with their original filenames with '_t' suffix

### Features:

- Transposes dates so each row has a date, country, and case/death data both absolute and per capita
- Creates `us_cause_of_death_2015_t.csv` from CDC 2015 data listing the top 5 causes of death per state absolute and per capita
- Adds lockdown and tracing data to global output files (must be manually updated from `https://ourworldindata.org/grapher/covid-contact-tracing`
- All output files should be easily joined with other tables including `population_table.csv`

### Major Bugs
9/10/2020: Per capita for confirmed cases in US doesn't have population column so it shows -1, probably causes some slight date data corruption as well

### Superficial Bugs
Bonaire and surrounding islands incorrectly interpreted.
Congo incorrectly interpreted.

### Potential Enhancements
Add arguments for different data transformation options
Add better column interpretation (quotes with or without commas)
Consolidate files with shared functions

### Notes
Read sources.txt for direct links to different data sources
Thank you