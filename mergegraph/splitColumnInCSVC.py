import sys
import csv

# Given a CSV file and a column number (0 based),
# split this column in 2.
# The column indicated contains an XPath, and the new column will contain
# the last element of the XPath. The indicated column is not changed.
#
# Example - original column looks like this:
# Root/CaseSummary/CaseID;...
#
# New column is added next to the original one:
# Root/CaseSummary/CaseID; CaseID;...

def readCSVFile(filename):
    result = []

    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            result.append(row)

    return result

def writeCSV(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        csvwr = csv.writer(csvfile, delimiter=';')
        for row in data:
            csvwr.writerow(row)
    
    
if __name__ == "__main__":
    csvfile = sys.argv[1]
    columnno = int(sys.argv[2])
    newcolumnname = sys.argv[3]
    newfilename = sys.argv[4]
    
    headers = True
        
    csvdata = readCSVFile(csvfile)
    if headers:
        headrow = csvdata.pop(0)
        newmatrix = [headrow[0:columnno+1] + [newcolumnname] + headrow[columnno+1:]]
    
    for row in csvdata:
        path = row[columnno].split('/')
        newcolumndata = path.pop()
        newrow = row[0:columnno+1] + [newcolumndata] + row[columnno+1:]
        newmatrix.append(newrow)
    
    writeCSV(newmatrix, newfilename)
