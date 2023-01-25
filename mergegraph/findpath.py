import sys
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.json.jsontools import JSONTool

# I want to be able to insert a structure at a given point in a JSON structure.
# This given point could be a JSON Path, expressed as a slash separated string, e.g.:
# Declaration/properties/GoodsShipment/StatisticalValue.

# Read the paths to be merged into a JSON structure.
def readPaths(filename):
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
    
if __name__ == "__main__":
    # arg 1 is the CSV file containing the new paths.
    # arg 2 is the file containing the JSON structure I want to merge above paths into.
    pathsfile = sys.argv[1]
    jsonfile = sys.argv[2]
    jt = JSONTool()
    jsonobj = jt.readJSON(jsonfile)
     
    paths = readPaths(pathsfile)
    for path in paths:
        result = jt.findPathRecursive(jsonobj, path)
        print(path)
        if result is None:
            print('  Not found.')
        else:
            print('  Found.')