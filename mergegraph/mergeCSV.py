import sys
import csv

# Given 2 CSV files, merge them in a specific way, as described below.

def readCSVFile(filename):
    result = []

    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            result.append(row)

    return result

# Get column from matrix and return it as a list.
def getKeys(matrix, colno):
    idx = []
    
    for row in matrix:
        idx.append(row[colno])

    return idx

def makeJSONPath(mylist):
    jp = '/'.join([x for x in mylist if x is not None and len(x) > 0])
    return jp

def writeCSV(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        csvwr = csv.writer(csvfile, delimiter=';')
        for row in data:
            csvwr.writerow(row)
    
    
if __name__ == "__main__":
    csvfile1 = sys.argv[1]
    csvfile2 = sys.argv[2]
        
    csv1 = readCSVFile(csvfile1)
    csv2 = readCSVFile(csvfile2)
    
    pathindex = getKeys(csv1, 1)

    count = 0
    newmatrix = [['Note', 'XPath in merged DDNXA XML', 'Cardinality', 'Format/type', 'JSON Path in new structure', 'Comments']]
    for row in csv2:
        if row[0] in pathindex:
            count += 1
            rowidx = pathindex.index(row[0])
            if csv1[rowidx][0].lower() in ['v', 'x']:
                note = 'New'
            elif csv1[rowidx][0].lower() == 'e':
                note = 'Exists'
            else:
                note = csv1[rowidx][0]
            
            if row[0].strip().upper().startswith('ROOT/'):
                xpath = row[0].strip()
                xpath = xpath[5:]
            else:
                xpath = row[0]
                
            # Add row - see columns above where newmatrix is instantiated.
            newrow = [note, xpath, csv1[rowidx][6], csv1[rowidx][7]] 
            newrow.append(makeJSONPath(row[7:13]))
            newrow.append(row[13])
            newmatrix.append(newrow)
        else:
            print('ERROR:', row[0], 'not found. Row = ', row)
            
    print('Found', count, 'hits.')
    
    writeCSV(newmatrix, 'NewMapping_For_DDNXA.csv')
