import csv
##import keyboard as keys
##import gc
import sys
##import math
##from decimal import *
##from decimal import Decimal as d
from enum import Enum
from datetime import *
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
try:
    filename = sys.argv[1]
except:
    filename = "time_series_covid19_deaths_US"

CONVERT_TO_RATE = True #This is no longer current
ONE_WAVE_HERD = True
contact_tracing_filename = "covid-contact-tracing.csv"
other_death_causes_filename = 'LCWK9_2015.pdf'
sweden_population = int(0)

def other_causes(filename):
    # Open a PDF file.
    fp = open(filename, 'rb')
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        print(layout)

other_causes(other_death_causes_filename)
exit(0)

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
                             "Bonaire"
                             
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

    if count == 0: #Skip first row header
        row_array.append(row)
        count += 1
        continue

    if sub_count-8 > days: days = sub_count-8 #subtract first thirteen columns
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
##            if value == "Sweden": sweden_index = count # May as well get this here, while we're at it..
            parse_str = row_array[count-1][:row_array[count-1].find(',')]
##            print('!'+parse_str)
            if parse_str == value:
                addition = True
                print(parse_str + ':' + "Duplicate.. adding")               
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
    ####            print(value)
    ##            return_value = parseop(proc_row_array[count], ',', sub_count, 0, parse.REPLACE)            
            if sub_count > 9:
    ##            print("Subracting")
                return_value = parseop(_proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE)
                if return_value == -1:
                    print("Error subtracting")
                    exit(-1)
                    pass
                else:
                    _proc_row_array[count] = return_value
            elif sub_count == 9: #first value should always be averaged (this is for China)
    ##            print(value)
                return_value = parseop(_proc_row_array[count], ',', sub_count, _value/2, parse.REPLACE)
                _proc_row_array[count] = return_value

        _proc_row_array[count] = parseop(_proc_row_array[count], ',', sub_count, _value-prev_value, parse.REPLACE) #last data in series
        _proc_row_array[count] = _proc_row_array[count] + '\r' # carriage return

    return _proc_row_array    



if CONVERT_TO_RATE == True:
    row_array = convert_to_rates(row_array)



def compose_row(_row, _header_row, index, delimiter):
    global one_wave_herd
##    for i in range(1,20):
##        print(i, parseop(_row, delimiter, i, 0, parse.RETRIEVE))
    state = parseop(_row, delimiter, 1, 0, parse.RETRIEVE)
    lat = parseop(_row, delimiter, 3, 0, parse.RETRIEVE)
    lon = parseop(_row, delimiter, 4, 0, parse.RETRIEVE)
    pop = parseop(_row, delimiter, 8, 0, parse.RETRIEVE)
    day = parseop(_header_row, delimiter, index+6, 0, parse.RETRIEVE)
##    print(state, pop)
    day = day.replace('\r', '')


    
    deaths = float(parseop(_row, delimiter, index+8, 0, parse.RETRIEVE))
##    lockdown = "0"

##    deaths = deaths.replace('\r', '')
    if ONE_WAVE_HERD == True:
##        print (deaths, pop)
        if float(pop) > 0:
            deaths_per_capita =  float(float(deaths / float(pop))*100)
        else:
            deaths_per_capita = -1
        if deaths_per_capita > .057: print(state, deaths_per_capita) #This is slightly less than Sweden's recent %
##                lock_startday = population_table[row][2]
##                lock_endday = population_table[row][3]
##                if lock_startday != "":
##                    day_object = datetime.strptime(day, "%m/%d/%y")
##                    startday_object = datetime.strptime(lock_startday, "%m/%d/%y")
##                    if lock_endday != "":
##                        endday_object = datetime.strptime(lock_endday, "%m/%d/%y")
##                        if endday_object > day_object:
##                            if startday_object <= day_object:
##                                lockdown = "1"
##                                print(lock_startday, day)
##                print("Converting deaths for " + country)
    
    string = state + delimiter + lat + delimiter + lon + delimiter + str(day) + delimiter +\
    str(deaths) + delimiter + str(deaths_per_capita) #+ delimiter + str(lockdown)
    return string


def transpose(_proc_row_array, _days):
    states = len(_proc_row_array)-1 #subtract header row
##    for s in range(1,states):
##        print(s, _proc_row_array[s][:10])
##    exit(0)
    print("Transposing for " +str(states) + " states across "+ str(_days) + " days...")
    _row_array = [None] * ((states) * (_days) + 1) #Add one for the header row

    #Compose Transposed Header Row:
    state = parseop(_proc_row_array[0], ',', 1, 0, parse.RETRIEVE)
    lat = parseop(_proc_row_array[0], ',', 3, 0, parse.RETRIEVE)
    lon = parseop(_proc_row_array[0], ',', 4, 0, parse.RETRIEVE)
    _row_array[0] = state + ',' + lat + ',' + lon + ',' + "Date" + ',' + 'Reported Deaths' + ',' + 'Deaths (Per Capita)' + '\r' #+ ',' + 'Lockdown' + '\r'

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
##exit(0)



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
        file_day = datetime.strptime(row['Date'], "%b %d, %Y")
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


##add_contact_tracing(row_array, ',')


csvfile_w = open(filename+'_t.csv', "w")
csvfile_w.writelines(row_array)
csvfile_w.close()

print('\n' + "Done, filename has _t suffix.")


