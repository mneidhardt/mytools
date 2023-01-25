import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.files.filetools import FileTools
from mytools.graph.graphs import EUCDMNode, Graph, EUCDMGraphTools

# Creates a dict from parts of the CSV Data.
# Key = xpath from csv
# Value = a list of the messages that this xpath are in.
def getPathAndMsgNumbers(csvdata):
    result = {}
    fieldnames = csvdata[0]
    
    for row in csvdata:
        xpath = row[5].replace('[0]', '')
        msgs = []
        for i in range(8, len(row)):
            if row[i].lower() == 'y':
                msgs.append(fieldnames[i])
        if xpath not in result:
            result[xpath] = msgs
        elif xpath in result and sorted(result[xpath]) == sorted(msgs):
            result[xpath] = msgs
        elif xpath in result:
            result[xpath] = result[xpath] + ['DUP>>>'] + msgs

    return result
    
def createXPaths(sgfilename, catalog):
    gtool = Graph()
    egt = EUCDMGraphTools(EUCDMNode)
    
    nodes = gtool.readSerialisedGraph(sgfilename)       # Read the basic serialised graph.
    annotatednodes = egt.annotateNodes(nodes, catalog)  # Annotate nodes with information from the catalog.
        
    graf = gtool.deserialiseGraphLoop(annotatednodes)
    
    xpaths = gtool.dfswp(graf)
    return xpaths
    
if __name__ == "__main__":
    sgfilename = sys.argv[1]            # Name of file containing serialised graph.
    datacatalogfilename = sys.argv[2]   # Name of file containing the data catalog.
    
    ft = FileTools()
    catalog = ft.readCSVFile(datacatalogfilename)       # Read the data catalog.
    xpaths = createXPaths(sgfilename, catalog)          # XPaths from the schema.

    if len(sys.argv) <= 3:
        for xpath in xpaths:
            print(xpath)
    else:
        docfilename = sys.argv[3]                   # The file name of the documentation with al XPaths and message associations.
                                                    # This is Emils excel-sheet, currently called Declaration.json_documentation_v4.7.0.csv
                                                    
        csvdata = ft.readCSVFile(docfilename)
        xpathdict = getPathAndMsgNumbers(csvdata)           # XPaths from the Import/Export/Transit documentation, 
                                                            # including ref to individual messages that the element appears in.
        
        for xpath in xpaths:
            xpath2 = '$.'+xpath
            if xpath2 in xpathdict:
                print(xpath, xpathdict[xpath2])
            else:
                print('NotFound', xpath)
        
        #for row in csvdata:
        #    print(row[5],row[8:])
        #    break
