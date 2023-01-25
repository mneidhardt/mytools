import sys
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.xml.xmlparsing import XMLParser

# Given an XML file, find each XPath and the text for the leaf.
# Perhaps this should also return text for intermediate nodes?
# Also, given a CSV file with the XML, the texts are added to the CSV, using the xpath as key.

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
    # Args: [1] is the XML file.
    xmlfile = sys.argv[1]
    csvfile = sys.argv[2]
        
    xmlparser = XMLParser(xmlfile)
    csvdata = readCSVFile(csvfile)
    
    texts = xmlparser.getAllTextContent()
    uniqtexts = {}
    for text in texts:
        ids = text.split(',')
        for id in ids:
            uniqtexts[id] = 1
    uniqtexts = sorted(list(uniqtexts))
    
    # First row is column names, so use that as basis for new matrix:
    columnnames = csvdata.pop(0)
    columnnames.extend(uniqtexts)
    newmatrix = [columnnames]
    
    for row in csvdata:
        if row[0] == 'LEVEL':
            newmatrix.append(row)
        else:
            # Find this xpath in the XML, to get the name of the IEs where it appears:
            xp = xmlparser.findPath('./' + row[1])
            if len(xp) != 1:
                print('ERROR: 1+ found: ', row[0])
            else:
                # These are the IEs of the current XPath:
                ids = xp[0].text.split(',')
                
                for ut in uniqtexts:
                    if ut in ids:
                        row.append('Y')
                    else:
                        row.append('')                        
                    
                newmatrix.append(row)

    writeCSV(newmatrix, 'NewMappingWithIEPresence_For_DDNXA.csv')
