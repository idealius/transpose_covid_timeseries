import csv
import sys
from enum import Enum
from datetime import *
from io import StringIO

from pdfminer3.converter import TextConverter #I installed pdfminer3, this code was from https://pdfminersix.readthedocs.io/en/latest/tutorial/composable.html
from pdfminer3.layout import LAParams
from pdfminer3.pdfdocument import PDFDocument
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfparser import PDFParser

import re



try:
    filename = sys.argv[1]
except:
    filename = "time_series_covid19_confirmed_US"

CONVERT_TO_RATE = True #Versus Totals
ONE_WAVE_HERD = True
if CONVERT_TO_RATE == True:
    suffix = "_rate"
else:
    suffix = "_total"
contact_tracing_filename = "covid-contact-tracing.csv"
other_death_causes_filename = 'LCWK9_2015'
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

def writeblock(filename, data, suffix, extension):
    csvfile_w = open(filename+suffix + extension, "w")
    csvfile_w.writelines(data)
    csvfile_w.close()

def writestuff(file, data):
    datawriter = csv.writer(file)
    datawriter.writerow(data)
    return


def parsestuff(string, delimiter):
    _string = string+',' #Add a trailing comma at end of complete line to account for the last block

    while True:
        _chars = _string.find(delimiter)+1
        if _chars == -1 or _chars == 0: return "Error"
        yield _string[:_chars-1]
        _string = _string[_chars:]



class parse(Enum):
    INSERT = -4
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
    elif operation == parse.INSERT:
        string1 = string[:end+1]
        string2 = string[end+1:]
        return string1 + str(value) + delimiter + string2

    return string1 + str(update_int) + string2


population_table = []

def load_population_table(_population_filename):
    global population_table
    try:
        csvfile = open(_population_filename, newline='')
        reader = csv.DictReader(csvfile)
    except:
        print("Please run sanitize_covid_state_deaths_total.py first to generate populations...")
        exit(-1)
    count = 0
    index = 0
    last_country = ""
    for row in reader:
        if count == 0:
            count +=1
            continue #skip first line, not sure if this is necessary but it shouldn't hurt
        if row['Province_State'] != last_country:
            population_table.append([row['Province_State'],row['Population']])
            print(population_table[index])
            index += 1
        last_country = row['Province_State']
        count += 1

print("Extracting populations from state deaths output...")
load_population_table("time_series_covid19_deaths_US_rate.csv")


row_array=[]
print("Processing File..")

throwaway = ["Diamond Princess", "MS Zaandam"]

count = 0
sub_count = 0
days = 0

#Retreive Rows and Consolidate Countries / Sanitize their names
for row in getstuff(filename, throwaway):

    for i in range(1,7): #Skip first 6 columns
        row=row[row.find(',')+1:] 

    if count == 0: #Append first row header and skip
        row_array.append(row)
        count += 1
        continue

    if sub_count-7 > days: days = sub_count-7 #subtract next 7 columns
    sub_count = 0


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

        
        if sub_count == 1: #Lets compare country name to the previous rows country
            parse_str = row_array[count-1][:row_array[count-1].find(',')]
            if value == '':  # No state??
                addition = False
                count -= 2
                break
##            print('!'+parse_str)
            if parse_str == value:
                addition = True
                print(parse_str + ':' + "Adding County...")               
            else: #If not the same country just add the row to our array
                row_array.append(row)
                break;
        elif sub_count > 7: #We're still here so it must be a duplicate country
##                print("Adding...")
            return_value = parseop(row_array[count-1], ',', sub_count, _value, parse.ADD)
            if return_value == -1:
##                print(parse_str)
                pass
            else: row_array[count-1] = return_value

    if addition != True: # Looks good, lets move to the next row...
        count +=1



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

            if sub_count > 8:
    ##            print("Subracting")
                return_value = parseop(_proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE)
                if return_value == -1:
                    print("Error subtracting")
                    exit(-1)
                    pass
                else:
                    _proc_row_array[count] = return_value
            elif sub_count == 8: #first value should always be averaged (this is for China)
    ##            print(value)
                return_value = parseop(_proc_row_array[count], ',', sub_count, _value/2, parse.REPLACE)
                _proc_row_array[count] = return_value

        _proc_row_array[count] = parseop(_proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE) #last data in series
        _proc_row_array[count] = _proc_row_array[count] + '\r' # carriage return

    return _proc_row_array    



if CONVERT_TO_RATE == True:
    row_array = convert_to_rates(row_array)


def other_causes(_row_array, filename, delimiter, num_causes):

    if num_causes < 1:
        num_causes = 1
    elif num_causes > 5:
        num_causes = 5

    causes_table = []

    causes_table.append("State, Cause 1, Cause 1 Value, Cause 1 Value (Per Capita)")

    for index in range(0, num_causes-1):
        causes_table[0] = causes_table[0] + delimiter + "Cause " + str(index+2) \
                                + delimiter + "Cause Value " + str(index + 2)\
                                + delimiter + "Cause Value " + str(index + 2) + " (Per Capita)"
        
    causes_table[0] = causes_table[0] + '\r'

    count = 1
    
    output_string = StringIO()
    print ("Processing other causes of death (2015)...")
    with open(filename + '.pdf', 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams(char_margin = 20))
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    text = str(output_string.getvalue())
    writeblock(filename, text, '.txt')

    skip_line = lambda str : -1 if str.find('\n') == -1 else str[str.find('\n')+1:]
    isolate_line = lambda str: -1 if str.find('\n') == -1 else str[:str.find('\n')]

    entry_value_per_capita = 0
    
    for row in _row_array:
        if row == _row_array[0]: continue
        
        state = parseop(row, ',', 1, 0, parse.RETRIEVE)
        pop = float(parseop(row, delimiter, 8, 0, parse.RETRIEVE))
        pattern = re.compile(state)
        search = pattern.search(text)
        if search == None: continue
##        print(entry1.end())
        placeholder_string = text[search.end():]

        #find first cause of death value
        if state == "Maryland": lines = 7
        else: lines = 3
        
        for i in range(0,lines): #Skip first 3 lines
            return_value = skip_line(placeholder_string)
            if return_value == -1: exit(-1)
            placeholder_string = return_value

        #First cause of death value (the values come before the labels)
        entry_value = placeholder_string[:placeholder_string.find(' ')]
        for i in range(0,10): entry_value = entry_value.replace(',', '') #Remove up to 9 commas

        causes_line = state
        
        for index in range(0, num_causes):
  
            #find cause of death label
            placeholder_string = skip_line(placeholder_string) #skip another line
            entry_name = isolate_line(placeholder_string) #isolate it

            pattern = re.compile("\D+(?= )")
            search = pattern.search(entry_name)
            if search == None:
                print("Name not found..")
            else:
                entry_name = search.group()
                entry_name = entry_name[1:] # remove prefix space

            if pop > 0:
                entry_value_per_capita = float(float(float(entry_value) / pop) * 100)
            else:
                entry_value_per_capita = -1

            #Add to table
            causes_line = causes_line + delimiter + entry_name + delimiter + entry_value \
                                  + delimiter + str(entry_value_per_capita)
       

            #fine next cause of death value
            placeholder_string = skip_line(placeholder_string) #skip another line
            entry_value = placeholder_string[:placeholder_string.find(' ')]
            for i in range(0,10): entry_value = entry_value.replace(',', '')
            
        causes_table.append(causes_line + '\r')
        count += 1

        
##        print(state, entry_name, entry_string)
            
##    print(causes_table)
    writeblock("us_cause_of_death_2015", causes_table, '.csv')

    
#We don't need this because this is cases:
    
##other_causes(row_array, other_death_causes_filename, ',', 5)


def compose_row(_row, _header_row, index, delimiter):
    global one_wave_herd
    global population_table

    state = parseop(_row, delimiter, 1, 0, parse.RETRIEVE)
    lat = parseop(_row, delimiter, 3, 0, parse.RETRIEVE)
    lon = parseop(_row, delimiter, 4, 0, parse.RETRIEVE)

    day = parseop(_header_row, delimiter, index+5, 0, parse.RETRIEVE)

    day = day.replace('\r', '')

    pop = "-1"
    
    cases = float(parseop(_row, delimiter, index+7, 0, parse.RETRIEVE))

    if ONE_WAVE_HERD == True:
        #look up population by state
        count = 0
        for index in range(0, len(population_table)):
            if population_table[index][0] == state:
                pop = population_table[index][1]
                break
                           
        if float(pop) > 0:
            cases_per_capita =  float(float(cases / float(pop))*100)
        else:
            cases_per_capita = -1
        if cases_per_capita > .057: print(state, cases_per_capita) #This is slightly less than Sweden's recent % for deaths

    
    string = state + delimiter + lat + delimiter + lon + delimiter + str(day) + delimiter +\
    str(cases) + delimiter + str(cases_per_capita) + delimiter + pop
    return string


def transpose(_proc_row_array, _days):
    states = len(_proc_row_array)-1 #subtract header row

    print("Transposing for " +str(states) + " states across "+ str(_days) + " days...")
    _row_array = [None] * ((states) * (_days) + 1) #Add one for the header row

    #Compose Transposed Header Row:
    state = parseop(_proc_row_array[0], ',', 1, 0, parse.RETRIEVE)
    lat = parseop(_proc_row_array[0], ',', 3, 0, parse.RETRIEVE)
    lon = parseop(_proc_row_array[0], ',', 4, 0, parse.RETRIEVE)
    _row_array[0] = state + ',' + lat + ',' + lon + ',' + "Date" + ',' + 'Reported Cases' + ',' + 'Cases (Per Capita)' \
                            +','+ 'Population'+ '\r' #+ ',' + 'Lockdown' + '\r'

    #Transpose the rest:
    for c in range(1, states+1):
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

row_array = transpose(row_array, days)
##print(row_array)


writeblock(filename, row_array, suffix, '.csv')

print('\n' + "Done, filename has " + suffix + " suffix.")


