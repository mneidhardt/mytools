import sys
import re
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import Graph


class CSVTool():
    # Read a file line by line.
    def readFilelines(self, filename):
        result = []
        with open(filename) as f:
            for line in f:
                parts = line.strip().split(' ')
                result.append(parts)
        return result

    def readCSVFile(self, filename, delimchar=';'):
        result = []

        with open(filename) as csvfile:
            crdr = csv.reader(csvfile, delimiter=delimchar)
            for row in crdr:
                result.append(row)

        return result

    def writeCSVFile(self, csvdata, filename):
        with open(filename, 'w', newline='') as csvfile:
            mywriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='|')
            for row in csvdata:
                mywriter.writerow(row)

    def lookupString(self, table, columnid, string):
        result = []
        for row in table:
            if string == row[columnid]:
                result.append(row[0])
        return result

    def lookupKey(self, table, columnid, key):
        result = []
        for row in table:
            if key == row[columnid]:
                result.append(row[5])
        return result

    # Lookup row in datacatalog based on key.
    # If found, returns name and format for the key.
    # These are found in column 5 and 3 of the datacatalog respectively.
    def lookupNameAndFormat(self, key, table):
        for row in table:
            if key == row[0]:
                return [row[5], row[3]]

        return []

# Expand datacatalog with names only in DDNXA/DDNTA:
def task1(datacatalogfile, extradatafile):
    # datacatalogfile =  # The original csv data.
    # extradatafile = # The data to be added to the original.

    ct = CSVTool()
    csvdata = ct.readCSVFile(datacatalogfile)
    if len(csvdata[0]) != 7:
        print('CSV != 7:', csvdata[0])
        
    extradata = ct.readFilelines(extradatafile)

    primarykey = 509
    
    for row in extradata:
        if row[3].strip().upper() == 'DDNXA':
            domain = 'E'
        elif row[3].strip().upper() == 'DDNTA':
            domain = 'T'
        else:
            domain = '???'+row[3]
        
        newrow = [primarykey, None, row[2], None, None, row[2], domain]
        csvdata.append(newrow)
        primarykey += 1
    
    ct.writeCSVFile(csvdata, 'datacatalog.withExtras.csv')

# Replace '?A' with primary key from expanded datacatalog.
def task2(serialgraffile, datacatalogfile):
    ct = CSVTool()
    
    sg = ct.readFilelines(serialgraffile)
    catalog = ct.readCSVFile(datacatalogfile)
    numpattern = re.compile('^\s*\d+\s*$')
    
    for line in sg:
        if line[0] == '!':
            print(line[0])
        elif line[0].startswith('?A'):
            pk = ct.lookupString(catalog, 5, line[1])
            if len(pk) == 1:
                print(pk[0])
            else:
                print(line, ' >>> ', pk)
        elif numpattern.match(line[0]):
            print(line[0])
        else:
            print(line)

def dummyNodes():
    nodes = []
    nodes.append(('1', 1, 1))
    nodes.append(('577', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('544', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('545', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('591', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('554', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('599', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('566', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('565', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('562', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('590', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('592', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('594', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('555', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('582', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('560', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('561', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('564', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('602', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('518', 1, 1))
    nodes.append(('?EreferenceNumber', 1, 1))
    nodes.append(('?DAdditionalProcedure', 1, 99))
    nodes.append(('?A1sequenceNumberDDNXA', 1, 1))
    nodes.append(('29', 1, 1))
    nodes.append(('?DPreviousDocument', 1, 99))
    nodes.append(('?A1sequenceNumberDDNXA', 1, 1))
    nodes.append(('!', 0, 0))
    nodes.append(('!', 0, 0))
    nodes.append(('!', 0, 0))
    nodes.append(('!', 0, 0))
    nodes.append(('!', 0, 0))
    nodes.append(('!', 0, 0))
    nodes.append(('!', 0, 0))
    return nodes

# This is a subtask for task3 and task4.
# NB: The nodes that are the input to deserialiseGraph should only contain
# the key in tupl element 0. For display purposes I here use names as element 0.
def subtask3(serialgraffile, datacatalogfile):
    gt = Graph()
    nodes = gt.readSemiSerialisedGraph(serialgraffile)
    
    ct = CSVTool()
    
    catalog = ct.readCSVFile(datacatalogfile)
    nodeswithnames = []
    for node in nodes:
        name = ct.lookupKey(catalog, 0, node[0])
        if len(name) >= 1:
            newname = name[0]
        else:
            newname = node[0]
        nodeswithnames.append((newname, node[1], node[2]))
        
    graf = gt.deserialiseGraphLoop(nodeswithnames)

    return graf

# Since I am impatient, I wanted to read the serialised graph, before it
# was complete, i.e. some nodes have only name and no key. So this reads a semiserialised graph
# and shows it.
def task3(serialgraffile, datacatalogfile):
    graf = subtask3(serialgraffile, datacatalogfile)
    gt = Graph()
    gt.showGraph(graf)

    return graf
    
# I want to generate the full xpath for each node, so I can look it up in Emils Excel/CSV file
# which will give us extra info.
# This first creates the graph, and from that a list of xpaths. The graph is in this case made from a semiserialised graph..
def task4(serialgraffile, datacatalogfile):
    gt = Graph()
    nodes = gt.readSemiSerialisedGraph(serialgraffile)
    
    ct = CSVTool()
    
    # Here I amend the nodes with name and fomat.
    # This will relace the function annotateNodes in the buildJsonSchema script.
    # Thi could probably take place in readSemiSerialisedGraph? Needs the data catalog, of course.
    catalog = ct.readCSVFile(datacatalogfile)
    extendednodes = []
    for node in nodes:
        if node[0] == '!':
            extendednodes.append((node[0], node[1], node[2], None, None))
        else:
            nf = ct.lookupNameAndFormat(node[0], catalog)
            if len(nf) == 2:
                extendednodes.append((node[0], node[1], node[2], nf[0], nf[1]))
            else:
                extendednodes.append((node[0], node[1], node[2], '<NONAME>'+node[0], None))

    graf = gt.deserialiseGraphLoop(extendednodes)

    gt.showGraph(graf)
    #paths = gt.dfswp(graf)
    #for path in paths:
    #    print(path)

if __name__ == "__main__":
    #task3(sys.argv[1], sys.argv[2])
    task4(sys.argv[1], sys.argv[2])
    
