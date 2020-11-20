import csv
import sys
from enum import Enum
from datetime import *
from io import StringIO
import pandas as pd
import json

# Creates JSON and JS files from CSV

try:
    filename = sys.argv[1]
except:
    filename = "time_series_covid19_confirmed_US_rate"

def csv_debug(filename):
    with open(filename+".csv", 'r') as f:
        reader = csv.reader(f)
        linenumber = 1
        try:
            for row in reader:
                linenumber += 1
        except Exception as e:
            print (("Error line %d: %s %s" % (linenumber, str(type(e)), e.message)))
    return


# csv_debug(filename)
df = pd.read_csv (filename + '.csv', engine='python')
with pd.option_context('display.precision', 15):
    print(df)
filename = filename.replace("time_series_", "")
# df = 'var' + filename + ' = '+ df
# df.to_json (filename + '.json', orient="records", double_precision=30)

# json.dumps(df.to_dict())
f = open(filename + '.json','w')
json.dump(df.to_dict(orient="records"), f)  # f is an open fileobj
f.close()
f = open(filename + '.json','r')
newf = open(filename + '.js','w')
lines = f.readlines() # read old content
first_line = newf.write('var ' + filename + ' = ' + lines[0]) # write new content at the beginning
i = 0
for line in lines: # write old content after new
    if i == 0: continue
    newf.write(line)
    i += 1
newf.close()
f.close()
