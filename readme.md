# Sanitize COVID-19 Data

Downloads time series data for deaths and confirmed cases from John Hopkins COVID-19's github. 
Then, sanitizes and transposes it so it is workable in common visualization software (Excel, Tableau, QGIS, etc.) for a timelapse and writes to a file with absolute values and per capita values **in percent (multiplied by 100.)**

### Requirements

- Windows 10 (Maybe Windows 8/7 would work)
- Some CSV reading ability (Excel, LibreOffice Calc, Google Sheets, etc.)

### Features:
- Converts totals to rates as it is usually easier to add a running total in use cases versus determining a rate from a total
- Transposes dates so each row has a date, country, and case/death data both absolute and per capita
- Creates `us_cause_of_death_2015_t.csv` from CDC 2015 pdf data listing the top 5 causes of death per state absolute and per capita
- Adds lockdown and contact tracing data to world output files (must be manually updated from `https://ourworldindata.org/grapher/covid-contact-tracing`)
- All output files should be easily joined with other tables, e.g. `population_table.csv`

### Instructions

1. Install Python 3.x
(https://www.python.org/downloads/)

2. Install pdfminer3. From command line:

`pip3 install pdfminer3`

3. Install wget, add to PATH, then run `downloadcovid.bat`
- OR-
Right-click `downloadcovid.ps1` then click Run with Powershell

4. From command line run one of the python scripts:

`python sanitize_covid_data_cases.py`

or

`sanitize_covid_data_cases.py`

or for running all of them:

`sanitize_covid\sanitize_data`

5. Files saved with their original filenames with '_t' suffix

### FAQ:
Q. What do the different levels of Contract Tracing mean? (-1,0,1,2)

A.

-1 : No data

0 : None

1 : Some contact tracing

2 : All known cases contact traced

Source: `https://ourworldindata.org/grapher/covid-contact-tracing`

Q. Why are certain regions printed out during runtime and not others?

A. The regions are printed to the console if they have rates higher than sweden's total rate per capita. Other than that the rest is probably left over information used for debugging / confirmation. It's calculated on the fly for world data and hard-coded at .057% for state data comparison.

### Major Bugs
9/11/2020: None known

### Fixed Bugs
9/10/2020:
- Per capita for confirmed cases in US doesn't have population column so it shows -1, probably causes some slight date data corruption as well
- Congo Braz sanitized to "Congo", Congo Kinshasa sanitized to "Democratic Republic of Congo" to be consistant with contact tracing csv

### Superficial Bugs
Bonaire and surrounding islands incorrectly interpreted.

US territories like Guam, Virgin Islands, etc. aren't accounted for correctly.

Bosnia and other territories are not handled correctly, a full list is outputted during processing and listed below in the limitations section.

Lat and Lon are taken from the first unique country / state which may be an undesirable region / county's lat and lon

### Potential Enhancements
Add scripts for rate conversion / transposing counties

Add arguments for different data transformation options

Add better column interpretation (quotes with or without commas)

Consolidate/refactor files with shared functions

### Limitations
1. The scripts have basic adaptation in a few places, but they rely heavily on the source csv files maintaining the same format, (e.g. the same number of columns matters a lot, but not the column names in certain cases.) **This means the scripts can immediately break because an author of the original CSV files changed something seemingly simple.** Just today they changed the confirmed (state) cases to have a couple of extra rows, one with what I believe to be a total and it broke the script.
2. Must run state death python to retrieve population data for state cases.
3. The contact tracing data must be downloaded manually, and they changed the date format on me once already, so it might need periodic code modification to maintain.
4. China has data before 1/22 that can't be included because John Hopkins / Institutions did not include it so the rate for the first date (1/22) is halved to adjust for this
5. Execution speed is not a high priority since it only needs to be ran once per day. Also, sometimes there is duplicate file reading/writing (such as with the PDF interpretation of top causes of death) and calculations. The whole thing should only take a couple of minutes to run, though.
6. Cruise ships "Diamond Princess", "MS Zaandam" culled from world data.
7. For world output, these regions need script adjustment for contact tracing / lockdown, or aren't releasing/tracking COVID data:
- Anguilla
- Aruba
- Bermuda
- Bosnia
- British (?)
- Cape
- Cayman
- Falkland
- Gibraltar
- Greenland
- Guam
- Hong
- Macao
- Montserrat
- Palestine
- Puerto
- Solomon
- Swaziland
- Timor
- Turkmenistan
- Turks
- Vanuatu



### Notes
Read sources.txt for direct links to different data sources

Thank you