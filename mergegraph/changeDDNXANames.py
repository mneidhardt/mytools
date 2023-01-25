import sys
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.json.jsontools import JSONTool

# Names in DDNXA XML follows different rules than the EUCDM names follow.
# E.g. DDNXA has elements such as:
#   CustomsOfficeOfExitActual &
#   summaryDeclarationRejectionReasonCode
#
# They must be converted to these:
#   Customs_office_of_exit_actual
#   Summary_declaration_rejection_reason_code.


# Read the paths/names to be changed.
def readPaths(filename):
    data = []

    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            data.append(row)
    return data

def readPaths2(filename):
    data = []

    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            if len(row) == 0:   # or row[0].lstrip().startswith('#'):
                continue
            else:
                # Do some cleanup:
                path = row[8].strip()
                if len(path) == 0:
                    continue
                path = path.split('/')
                if path[0].upper() == 'ROOT':
                    path.pop(0)
                if len(path) > 0:
                    data.append(path)
    
    data.pop(0) # Drop the headline.
    return data

def changeName(name):
    name = name.strip()
    newname = name[0].upper()
    
    for i in range(1, len(name)):
        if name[i].isupper():
            newname += '_' + name[i].lower()
        else:
            newname += name[i]

    return newname
    
    
if __name__ == "__main__":
    # arg 1 is the CSV file containing the new paths.
    pathsfile = sys.argv[1]
     
    csvmatrix = readPaths(pathsfile)
    for row in csvmatrix:
        if len(row[8].strip()) > 0:
            path = row[8].split('/')
            newpath = []
            for e in path:
                if e == 'ROOT':
                    continue
                else:
                    newpath.append(changeName(e))
            row.append(';'.join(newpath))
        else:
            row.append('')
        print(';'.join(row))