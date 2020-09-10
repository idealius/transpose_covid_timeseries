#### Sanitize COVID-19 Data

Downloads time series data for deaths and confirmed cases from John Hopkins COVID-19's github
Then, sanitizes it so it is workable in common visualization software (Excel, Tableau, QGIS, etc.) and writes to a file with absolute values and per capita values.

Requirements: Windows 10 (Maybe Windows 8/7 would work)

Instructions:


1. Install Python 3.x
(https://www.python.org/downloads/)

2. Install wget, add to PATH, then run 'sanitize_covid\downloadcovid.bat'
- OR-
Right-click 'sanitize_covid\downloadcovid.ps1' then click Run with Powershell

3. From command line e.g. run

'python sanitize_covid_data_cases.py'

or

'sanitize_covid_data_cases'

or for running all of them:

'sanitize_covid\sanitize_data'

4. Files saved with their original filenames with '_t' suffix