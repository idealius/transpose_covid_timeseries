import csv
##import keyboard as keys
##import gc
import sys
##import math
##from decimal import *
##from decimal import Decimal as d
from enum import Enum

try:
    filename = sys.argv[1]
except:
    filename = "time_series_covid19_deaths_global"



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
##        print('c-'+str(_chars))
##        print('!' + _string[:_chars-1])
        yield _string[:_chars-1]
        _string = _string[_chars:]
##        print('%'+_string)

class parse(Enum):
    RETRIEVE = -3
    REPLACE = -2
    ADD = -1


def parseop(string, delimiter, index, value, operation): #parse operation, index starts at 1
    _string = string+','#Add a trailing comma at end of complete line to account for the last block
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
 
##    print(start)
##    print(end)
##    print((string[start:end]))
##    print(count, index, start, end, '#'+str(value)+'#')
##    print(string, '!'+string[start:end]+'!')
    if operation == parse.REPLACE:
        update_int = value
        string1 = string[:start]
        string2 = string[end:]
    elif operation == parse.ADD:    
        update_int = int(string[start:end]) + int(value)
        string1 = string[:start]
        string2 = string[end:]
    elif operation == parse.RETRIEVE:
        return string[start:end]
    return string1 + str(update_int) + string2


def sanitize_countryname(string):
    culprits = ["\"", #Get rid of extra commas
                    "\*", #Get rid of the * in Taiwan
                    "Korea, South",
                    "Bosnia and Herzegovina",
                    "Congo (Brazzaville)",
                    "Congo (Kinshasa)",
                    "Taiwan*",
                    "Bonaire, Sint Eustatius and Saba"
]
    
    replacements = ["",
                             "",
                             "South Korea",
                             "Bosnia",
                             "Democratic Republic of Congo",
                             "Democratic Republic of Congo",
                             "Taiwan",
                             "Bonaire Sint Eustatius and Saba"
]
    
    count = 0
    for item in culprits:
        string = string.replace(item, replacements[count])
        count += 1

    return string



row_array=[]
print("Processing File..")

throwaway = ["Diamond Princess", "MS Zaandam"]

count = 0


#Retreive Rows and Consolidate Countries
for row in getstuff(filename, throwaway):

    row=row[row.find(',')+1:] #Skip first column

    if count == 0: #Skip first row header
        row_array.append(row)
        count += 1
        continue
    
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
##            print('~'+value+'~')
        
        if sub_count == 1: #Lets compare country name to the previous rows country
            parse_str = row_array[count-1][:row_array[count-1].find(',')]
                #print('!'+parse_str)
            if parse_str == value:
                addition = True
                print(parse_str + ':' + "Duplicate.. adding")
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
print("Converting from totals to rates...")
count = 0
proc_row_array=[None] * len(row_array)

#Remove trailing commas and convert from totals to per day rates
for count in range(0, len(row_array)):
    proc_row_array[count] = row_array[count]

    if  count == 0: #Skip header row
        proc_row_array[count] =proc_row_array[count] + '\r' # carriage return
        continue
##    print(row)
    sub_count = 0
    _value = 0
    for value in parsestuff(row_array[count], ','):
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
            return_value = parseop(proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE)
            if return_value == -1:
                print("Error subtracting")
                exit(-1)
                pass
            else:
                proc_row_array[count] = return_value
        elif sub_count == 4: #first value should always be averaged (this is for China)
##            print(value)
            return_value = parseop(proc_row_array[count], ',', sub_count, _value/2, parse.REPLACE)
            proc_row_array[count] = return_value

    proc_row_array[count] = parseop(proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE) #last data in series
    proc_row_array[count] = proc_row_array[count] + '\r' # carriage return
    
##print(proc_row_array)
##exit(0)
#Compose final format

def compose_row(_row, _header_row, index, delimiter):
    country = parseop(_row, delimiter, 1, 0, parse.RETRIEVE)
    lat = parseop(_row, delimiter, 2, 0, parse.RETRIEVE)
    lon = parseop(_row, delimiter, 3, 0, parse.RETRIEVE)

    day = parseop(_header_row, delimiter, index+3, 0, parse.RETRIEVE)
    day = day.replace('\r', '')
    deaths = parseop(_row, delimiter, index+3, 0, parse.RETRIEVE)
    deaths = deaths.replace('\r', '')  
    string = country + delimiter + lat + delimiter + lon + delimiter + str(day) + delimiter + str(deaths)
    return string

##try:
##    count = 0
##    c = 0
##    while c != -1:
##        count +=1
##        c = print(str(parseop(proc_row_array[0], ',', count, 0, parse.RETRIEVE)))
##except:
##        print('!' + str(count))

days = sub_count-3 #subtract first three columns
countries = len(proc_row_array)-1 #subtract header row
print("Transposing for " +str(countries) + " countries across "+ str(days) + " days...")
final_row_array = [None] * ((countries) * (days) + 1) #Add one for the header row

#Compose Transposed Header Row:
country = parseop(proc_row_array[0], ',', 1, 0, parse.RETRIEVE)
lat = parseop(proc_row_array[0], ',', 2, 0, parse.RETRIEVE)
lon = parseop(proc_row_array[0], ',', 3, 0, parse.RETRIEVE)
final_row_array[0] = country + ',' + lat + ',' + lon + ',' + "Date" + ',' + 'Deaths' + '\r'

#Transpose the rest:
for c in range(1, countries+1):
    for index in range(1, days+1):
##        if c * days + index + 1 >= len(final_row_array): break;
        try:
            final_row_array[(c - 1) * (days)+index] = compose_row(proc_row_array[c], proc_row_array[0], index, ',') + '\r'
        except:
            print(str(c*days+index), str(len(final_row_array)-days))
##        print(final_row_array[c * days+index])
print(str((c-1)*days+index), str(len(final_row_array)))

csvfile_w = open(filename+'_t.csv', "w")
csvfile_w.writelines(final_row_array)
csvfile_w.close()

exit(0)
