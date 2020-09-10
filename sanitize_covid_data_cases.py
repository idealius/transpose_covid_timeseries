import csv
##import keyboard as keys
##import gc
import sys
##import math
##from decimal import *
##from decimal import Decimal as d
from enum import Enum
from datetime import *

try:
    filename = sys.argv[1]
except:
    filename = "time_series_covid19_confirmed_global"

CONVERT_TO_RATE = True 
ONE_WAVE_HERD = True
population_filename = "population_table.csv"
contact_tracing_filename = "covid-contact-tracing.csv"
sweden_population = int(0)

def getstuff(filename, criterion):
    with open(filename+'.csv', "r", newline='') as csvfile_r:
        datareader = csv.reader(csvfile_r, delimiter='\r')
        #yield next(datareader)  # yield the header row
        for row in datareader:
            throwaway = False
            for criteria in criterion:
                if criteria in row[0]: throwaway = True
            if throwaway == False:
##                print('^'+row[0])
                yield row[0]
        return

def writestuff(file, data):
    datawriter = csv.writer(file)
    datawriter.writerow(data)
    return

##def writeblock(file, data):
##    datawriter = csv.writer(file)
##    datawriter.writerow(data)
##    return

def parsestuff(string, delimiter):
    _string = string+',' #Add a trailing comma at end of complete line to account for the last block

    while True:
        _chars = _string.find(delimiter)+1
        if _chars == -1 or _chars == 0: return "Error"
        yield _string[:_chars-1]
        _string = _string[_chars:]



class parse(Enum):
    RETRIEVE = -3
    REPLACE = -2
    ADD = -1


def parseop(string, delimiter, index, value, operation): #parse operation, index starts at 1
    _string = string+delimiter#Add a trailing comma at end of complete line to account for the last block
    count = 1
    start = 0
    while count < index:
        block = _string.find(delimiter)+1
        if block == -1: return -1
        start += block
        #print (_string[segment:], '\n')
        _string = _string[block:]
        count += 1

    end = _string.find(delimiter)    
    if end == -1: return -1
    end += start
 
    if operation == parse.REPLACE:
        update_int = value
        string1 = string[:start]
        string2 = string[end:]#can't forget to remove the trailing comma
    elif operation == parse.ADD:    
        update_int = int(string[start:end]) + int(value)
        string1 = string[:start]
        string2 = string[end:]
    elif operation == parse.RETRIEVE:
        return string[start:end]
    return string1 + str(update_int) + string2


def sanitize_countryname(string):
    culprits = ["\"", #Get rid of extra quotes
                    "\*", #Get rid of the * in Taiwan
                    "Korea, South",
                    "Bosnia and Herzegovina",
                    "Congo (Brazzaville)",
                    "Congo (Kinshasa)",
                    "Bonaire, Sint Eustatius and Saba", #This one has problems because of the comma
                    "Czechia",
                    "Taiwan*"
                    
]
    
    replacements = ["",
                             "",
                             "South Korea",
                             "Bosnia",
                             "Democratic Republic of Congo",
                             "Democratic Republic of Congo",
                             "Bonaire",
                             "Czech Republic",
                             "Taiwan"
                             
]
    
    count = 0
    for item in culprits:
        string = string.replace(item, replacements[count])
        count += 1

    return string

def sanitize_contacttracing_countryname(string):
    culprits = ["Myanmar",
##                    "Congo",
                    "United States"
]
    
    replacements = ["Burma",
##                             "Democratic Republic of Congo",
                             "US"
]
    
    count = 0
    original_string = string
    for item in culprits:
        string = string.replace(item, replacements[count])
        if original_string != string: return string
        count += 1

    return string

population_table = []

def load_population_table(_population_filename):
    global sweden_population
    global population_table
    csvfile = open(_population_filename, newline='')
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        if row['Country'] == "Sweden":
            sweden_population =  int(row['Population'])
        population_table.append([row['Country'],row['Population'], row['Lockdown Start'], row['Lockdown End']])
        print(population_table[count])
        count += 1

load_population_table(population_filename)




row_array=[]
print("Processing File..")

throwaway = ["Diamond Princess", "MS Zaandam"]

count = 0
sub_count = 0
days = 0
sweden_index= 0
#Retreive Rows and Consolidate Countries / Sanitize their names
for row in getstuff(filename, throwaway):

    row=row[row.find(',')+1:] #Skip first column

    if count == 0: #Skip first row header
        row_array.append(row)
        count += 1
        continue

    if sub_count-3 > days: days = sub_count-3 #subtract first three columns
    sub_count = 0
    row = sanitize_countryname(row)


    addition = False
       
    for value in parsestuff(row, ','):
        try:
            _value = int(value)
            if _value == 0:
                sub_count += 1
                continue
        except:
            pass
            
        sub_count += 1 #sub_count starts at 1
##        print(sub_count)
##            print('~'+value+'~')
        
        if sub_count == 1: #Lets compare country name to the previous rows country
            if value == "Sweden": sweden_index = count # May as well get this here, while we're at it..
            parse_str = row_array[count-1][:row_array[count-1].find(',')]
                #print('!'+parse_str)
            if parse_str == value:
                addition = True
                print(parse_str + ':' + "Adding region...")               
            else: #If not the same country just add the row to our array
                row_array.append(row)
                break;
        elif sub_count > 3: #We're still here so it must be a duplicate country
##                print("Adding...")
            return_value = parseop(row_array[count-1], ',', sub_count, _value, parse.ADD)
            if return_value == -1:
##                    print("Stopped adding")
                pass
            else: row_array[count-1] = return_value

    if addition != True: # Looks good, lets move to the next row...
        count +=1

##print(row_array)

def find_sweden_per(_row_array, _sweden_index):
    high_total = 0
    for value in parsestuff(_row_array[_sweden_index], ','):
        try:
            high_total = int(value)
        except:
            pass
    print('Sweden\'s last value:' + str(high_total) + ' out of ' + str(sweden_population))
    return_value = float(float(high_total) / float(sweden_population))
    return return_value

one_wave_herd = find_sweden_per(row_array, sweden_index)
                

#Convert from totals to per day rates
def convert_to_rates(_row_array):
    print("Converting from totals to rates...")
    _proc_row_array=[None] * len(_row_array)
    for count in range(0, len(_row_array)):
        _proc_row_array[count] = _row_array[count]

        if  count == 0: #Skip header row
            _proc_row_array[count] =_proc_row_array[count] + '\r' # carriage return
            continue
    ##    print(row)
        sub_count = 0
        _value = 0
        for value in parsestuff(_row_array[count], ','):
            try:
                prev_value = _value
                _value = int(value)
            except:
                pass
                
            sub_count += 1 #sub_count starts at 1
    ####            print(value)
    ##            return_value = parseop(proc_row_array[count], ',', sub_count, 0, parse.REPLACE)            
            if sub_count > 4:
    ##            print("Subracting")
                return_value = parseop(_proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE)
                if return_value == -1:
                    print("Error subtracting")
                    exit(-1)
                    pass
                else:
                    _proc_row_array[count] = return_value
            elif sub_count == 4: #first value should always be averaged (this is for China)
    ##            print(value)
                return_value = parseop(_proc_row_array[count], ',', sub_count, _value/2, parse.REPLACE)
                _proc_row_array[count] = return_value

        _proc_row_array[count] = parseop(_proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE) #last data in series
        _proc_row_array[count] = _proc_row_array[count] + '\r' # carriage return

    return _proc_row_array    



if CONVERT_TO_RATE == True:
    row_array = convert_to_rates(row_array)


def compose_row(_row, _header_row, index, delimiter):
    global population_table
    global one_wave_herd
    country = parseop(_row, delimiter, 1, 0, parse.RETRIEVE)
    lat = parseop(_row, delimiter, 2, 0, parse.RETRIEVE)
    lon = parseop(_row, delimiter, 3, 0, parse.RETRIEVE)

    day = parseop(_header_row, delimiter, index+3, 0, parse.RETRIEVE)
    day = day.replace('\r', '')


    
    cases = float(parseop(_row, delimiter, index+3, 0, parse.RETRIEVE))
    cases_per_capita = 0
    lockdown = "0"

##    cases = cases.replace('\r', '')
    if ONE_WAVE_HERD == True:
        for row in range(0,len(population_table)):
##            print(population_table[row][0], country)
            if population_table[row][0] == country:
##                cases =  float(float(cases / float(population_table[row][1]) / one_wave_herd))
                cases_per_capita =  float(float(cases / float(population_table[row][1]))*100)
                if cases_per_capita > one_wave_herd: print(country, cases_per_capita) #Sweden's rate
                lock_startday = population_table[row][2]
                lock_endday = population_table[row][3]
                if lock_startday != "":
                    day_object = datetime.strptime(day, "%m/%d/%y")
                    startday_object = datetime.strptime(lock_startday, "%m/%d/%y")
                    if lock_endday != "":
                        endday_object = datetime.strptime(lock_endday, "%m/%d/%y")
                        if endday_object > day_object:
                            if startday_object <= day_object:
                                lockdown = "1"
##                                print(lock_startday, day)
##                print("Converting cases for " + country)
    
    string = country + delimiter + lat + delimiter + lon + delimiter + str(day) + delimiter +\
    str(cases) +delimiter + str(cases_per_capita) + delimiter + str(lockdown)
    return string


def transpose(_proc_row_array, _days):
    countries = len(_proc_row_array)-1 #subtract header row
    print("Transposing for " +str(countries) + " countries across "+ str(_days) + " days...")
    _row_array = [None] * ((countries) * (_days) + 1) #Add one for the header row

    #Compose Transposed Header Row:
    country = parseop(_proc_row_array[0], ',', 1, 0, parse.RETRIEVE)
    lat = parseop(_proc_row_array[0], ',', 2, 0, parse.RETRIEVE)
    lon = parseop(_proc_row_array[0], ',', 3, 0, parse.RETRIEVE)
    _row_array[0] = country + ',' + lat + ',' + lon + ',' + "Date" + ',' + 'Reported Cases' +',' + 'Cases (Per Capita)' + ',' + 'Lockdown' + '\r'

    #Transpose the rest:
    for c in range(1, countries+1):
        for index in range(1, _days+1):
    ##        if c * days + index + 1 >= len(_row_array): break;
            try:
                _row_array[(c - 1) * (_days)+index] = compose_row(_proc_row_array[c], _proc_row_array[0], index, ',') + '\r'
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
                print(str(c*_days+index), str(len(_row_array)-_days))
    ##        print(_row_array[c * days+index])
    print(str((c-1)*_days+index), str(len(_row_array)))
    return _row_array

##print(row_array)
##exit(0)
row_array = transpose(row_array, days)



def add_contact_tracing(_row_array, delimiter):
    csvfile = open(contact_tracing_filename, newline='')
    reader = csv.DictReader(csvfile)
    _row_array[0] = _row_array[0].replace('\r', '')
    _row_array[0] = _row_array[0] + delimiter + 'Contact Tracing' +'\r'
    print("Adding Contract Tracing Data...")
    file_country = ""
    file_position = 0
    skip = False
    file_line_count = 0
    next_country = True
    count = 0
    array_day = ""
    check_array_country = ""
    country_not_found = ""
    for row in reader:
        if file_line_count == 0:
            file_line_count += 1
            continue
        file_country = row["Entity"]
        file_country = sanitize_contacttracing_countryname(file_country)
##        file_day = datetime.strptime(row['Date'], "%b %d, %Y")
        file_day = datetime.strptime(row['Date'], "%Y-%m-%d")
        if file_country == country_not_found:
            continue
##        print (file_day)
        if skip == True: #Skip file lines if the country matches, but the day doesn't
            if file_day >= array_day:
                skip = False
            else:
                file_line_count += 1
                continue
        
        if count != 0: #double-check the Country hasn't suddenly changed on us
##            print(_row_array[count])
##            print(check_array_country, count)
            check_array_country = parseop(_row_array[count], delimiter, 1, 0, parse.RETRIEVE)
            check_array_country = check_array_country.replace('\r', '')

            day = parseop(_row_array[count], delimiter, 4, 0, parse.RETRIEVE)
            array_day = datetime.strptime(day, "%m/%d/%y")
            
            if check_array_country != file_country:
                skip = False
                next_country = True
            else:
                _row_array[count] = _row_array[count].replace('\r','')
                _row_array[count] = _row_array[count] + delimiter + row['Contact tracing (OxBSG)'] + '\r' #Repeated data assignment
##                print(_row_array[count])
                count += 1
          
       

        
        if next_country == True: #Find the country in our array
            count = 0
            for array_index in _row_array:
                if count == 0:
                    count += 1
                    continue
                array_country = parseop(_row_array[count], delimiter, 1, 0, parse.RETRIEVE)
                array_country = array_country.replace('\r', '')
                if file_country == array_country:
                    country_not_found = ""
                    next_country = False
##                    print("FOUND")
                    day = parseop(_row_array[count], delimiter, 4, 0, parse.RETRIEVE)
                    array_day = datetime.strptime(day, "%m/%d/%y")
                    if array_day > file_day:
                        skip = True
                    break
                count += 1
                if (count >= len(_row_array)):
                    print(file_country + ' not found in array.')
                    country_not_found = file_country
                    count = 0
                    break
                    

            file_line_count += 1
    #Fill in gaps of contact tracing data:
    total = 0
    for count in range(1,len(_row_array)):
        return_value = parseop(_row_array[count], ',', 8, 0, parse.ADD)
        if return_value == -1:
            _row_array[count] = _row_array[count].replace('\r', '')
            _row_array[count] = _row_array[count] + ',' + '-1' +'\r'
            total += 1
    print('\n' + str(total) + " missing contact tracing data points.")


add_contact_tracing(row_array, ',')


csvfile_w = open(filename+'_t.csv', "w")
csvfile_w.writelines(row_array)
csvfile_w.close()

print('\n' + "Done, filename has _t suffix.")


