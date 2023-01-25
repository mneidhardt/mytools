import json
import sys
import re
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.json.jsontools import JSONTool
from mytools.files.filetools import FileTools

# Look up denumber in table, in column 1.
# If found, and if column 5 is empty, insert name into column 5.
def addNameToTable(table, denumber, name):
    for i in range(0, len(table)):
        if table[i][1].strip() == denumber.strip():
            if table[i][5].strip() == '' or table[i][5].strip() == name.strip():
                table[i][5] = name
            else:
                print('NB: [', table[i][5], '] != ', name)
            return i

    return None

# My first version of the data catalog is simply the 508 elements from EUCDM 6.1.
# The names in this list are the ones from EUCDM, i.e. with spaces and its own capitalisation.
# The names now used in the JSON schema have been tailored for this use, and this script
# is made to add the JSON Schema names (that have a DENumber) to the data catalog.
# They are stored in column 5.
#
# Method: Read the Declaration as instance (produced by jsonschemaparser.py),
# instantiate it as a JSON object, and go through all keys, searching for patterns
# like "name>denumber".
# The name is the one used in the JSON Schema, and the denumber can be used as a lookup in the data catalog.
if __name__ == "__main__":
    filename = sys.argv[1]
    datacatalogfile = sys.argv[2]
    newdatacatalogfilename = sys.argv[3]
    
    jt = JSONTool()
    js = jt.readJSON(filename)
    keys = jt.allKeys(js)

   
    # Second, the names need processing.
    # They come from the schema, and contain a combination of name, description (which often contains DENumber and sometimes DDNXA or DDNTA),
    # and min and max cardinality.
    ft = FileTools()
    
    csvdata = ft.readCSVFile(datacatalogfile)

    denopattern = re.compile('^([^>]+)>(\d\d\s+\d\d\s+\d\d\d\s+\d\d\d)')
    ddnpattern = re.compile('^DDN[XT]A$', re.IGNORECASE)
    bothpattern = re.compile('^\d\d\s+\d\d\s+\d\d\d\s+\d\d\d[ ;]+DDN[XT]A$', re.IGNORECASE)

    for key in keys:
        match = denopattern.match(key)
        if match:
            rowid = addNameToTable(csvdata, match.group(2), match.group(1))
            if rowid is None:
                print('NoHit', match.group(1), '+', match.group(2))
    ft.writeCSVFile(csvdata, newdatacatalogfilename)