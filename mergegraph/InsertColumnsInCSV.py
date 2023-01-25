import sys
import csv

# Given 2 CSV files, A and B, and 2 numbers, C and D,
# add column D in A to B, provided that A and B has same value in column C on that row.
# C and D are 0 based indices into columns.

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
    csvfileA = sys.argv[1]
    csvfileB = sys.argv[2]
    columnC  = int(sys.argv[3])
    columnD  = int(sys.argv[4])
    newfilename = sys.argv[5]
    
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
