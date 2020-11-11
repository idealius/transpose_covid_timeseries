# Sanitize COVID-19 Data

Downloads time series data for deaths and confirmed cases from Johns Hopkins COVID-19's github. 
Then, sanitizes and transposes it so it is workable in common visualization software (Excel, Tableau, QGIS, etc.) for a timelapse and writes to a file with absolute values and per capita values **in percent (multiplied by 100.)**

### Requirements

- Windows 10 (Maybe Windows 8/7 would work)
- Python 3.x
- Some CSV reading ability (Excel, LibreOffice Calc, Google Sheets, etc.)

### Features:
- Converts US county data to state data
- Converts province data to country data 
- Versions of scripts to run totals or rates of deaths/cases (9/19/20 update)
- Transposes dates so each row has a date, country, and case/death data both absolute and per capita
- Creates `us_cause_of_death_2015_t.csv` from CDC 2015 pdf data listing the top 5 causes of death per state absolute and per capita
- Adds lockdown and contact tracing data to world output files (must be manually updated from `https://ourworldindata.org/grapher/covid-contact-tracing`)
- All output files should be easily joined with other tables, e.g. `population_and_lockdown_table.csv`

### Instructions

1. Install Python 3.x
(https://www.python.org/downloads/)

2. Install pdfminer3. From command line:

`pip3 install pdfminer3`

*Note: for JSON and JS rate outputs also `pip3 install pandas`

3. Right-click `downloadcovid.ps1` then click Run with Powershell
- OR Install wget, add to PATH, then run `downloadcovid.bat`


4. From command line run one of the python scripts:

e.g.

`python sanitize_covid_data_world_cases.py`

or

`sanitize_covid_data_world_cases.py`

or for running all of them:

`sanitize_data.bat`

or for downloading and running all of them (wget required):

`new_day_rate.bat`

`new_day_total.bat`

or


`new_day_both.bat`


5. Files saved with their original filenames with 'total' or 'rate' suffix

### FAQ:
Q. What do the different levels of Contract Tracing mean? (-1,0,1,2)

A.

-1 : No data

0 : None

1 : Some contact tracing

2 : All known cases contact traced

Source: (https://ourworldindata.org/grapher/covid-contact-tracing)

Q. Why are certain regions printed out during runtime and not others?

A. The regions are printed to the console if they have rates higher than sweden's total rate per capita. Other than that the rest is probably left over information used for debugging / confirmation. It's calculated on the fly for world data and hard-coded at .057% for state data comparison. The usefulness of this is questionable for the rate scripts (vs the totals.)

Q. Why does it say "Sweden's last value x of y?"

A. This is the last **total** of cases or deaths for Sweden. I somewhat arbitrarily chose it as a litmus test for other regions. You can ignore it as it doesn't affect the output data.

### Major Bugs / New Major Features
11/11/2020: Added .py and .bat files for json and js data outputs for rates data global / US and appended to new_day_both.bat

9/30/2020: None known

### Fixed Bugs / New Features
11/11/2020: Changed states python scripts behavior to only print one "Adding County..." for each state in attempt to speed up state scripts and make less verbose.

9/30/2020: Fixed major bug from last update where the rates were not executed by new_day_rate / new_day_both nor the respective python scripts

9/14/2020: Fixed major bug where the all leading causes of death value was replacing the leading cause of death

9/11/2020:
- Per capita for confirmed cases in US doesn't have population column so it shows -1, probably causes some slight date data corruption as well
- Congo Brazzaville sanitized to "Congo", Congo Kinshasa sanitized to "Democratic Republic of Congo" to be consistent with contact tracing csv
- Fixed Bosnia
- Fixed rare bug with extra ghost column being added during contact tracing processing

### Superficial Bugs
Bonaire and surrounding islands interpreted incorrectly due to a comma within its label.

US territories like Guam, Virgin Islands, etc. aren't accounted for correctly because they lack population table data.

A full list of territories with population data that isn't cross-referenced correctly with COVID-19 data is outputted during processing and listed below in the limitations section below.

Lat and Lon are taken from the first unique country / state which may be an undesirable region / county's lattitude and longitude

### Potential Enhancements
Add saving rates and totals to each case/death output file (9/19/20 I decided to just duplicate the scripts because it seemed more timely)

Add scripts for county (not count**r**y) rate conversion / transposing

Add arguments for different data transformation options

Add better column interpretation (quotes with or without commas)

Consolidate/refactor files with shared functions

### Limitations
1. The scripts have basic adaptation in a few places, but they rely heavily on the source csv files maintaining the same format, (e.g. aside from the dates, the same number of columns matters a lot, but not the column names in certain cases.) **This means the scripts can immediately break because an author of the original CSV files changed something seemingly simple.** Just today they changed the confirmed (state) cases to have a couple of extra rows, one with what I believe to be a total and it broke the script which required fixing. Additionally, the contact tracing data must be downloaded manually, and they changed the date format on me once already, so it might need periodic code modification to maintain.
2. Must run state death python script to retrieve population data for state cases python script.
3. China has data before 1/22 that can't be included because Johns Hopkins / reporting institutions did not include it so the rate for the first date (1/22) is halved to adjust for this
4. Execution speed is not a high priority since it only needs to be ran once per day. Also, sometimes there is duplicate file reading/writing (such as with the PDF interpretation of top causes of death) and calculations.
5. Cruise ships "Diamond Princess", "MS Zaandam" culled from world data.
6. For world output, these regions need script adjustment for contact tracing / lockdown, or aren't releasing/tracking COVID data:
- Anguilla
- Aruba
- Bermuda
- British Virgin Islands
- Cape Verde
- Cayman Islands
- Falkland Islands
- Gibraltar
- Greenland
- Guam
- Hong Kong
- Macao
- Montserrat
- Palestine
- Puerto Rico
- Solomon Islands
- Swaziland
- Timor
- Turkmenistan
- Turks and Caicos Islands
- Vanuatu



### Sources & Notes
#### Country Data

Johns Hopkins Death and Confirmed Cases Data:

(https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv) 

(https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv) 

Lockdown Data (Updated 8/22/2020):

(https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdowns)

Contact Tracing Data:

(https://ourworldindata.org/grapher/covid-contact-tracing)

Country Population Totals (Updated 8/22/2020):

(https://www.worldometers.info/world-population/population-by-country/)


#### State Data

Johns Hopkins Death and Confirmed Cases Data:

(https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv) 

(https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv) 

2015 Cause of death data:

(https://www.cdc.gov/nchs/nvss/mortality/lcwk9.htm)

Thank you