import sys
import pathlib
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.json.jsontools import EUCDMXMLJSONMapperTool
from mytools.xml.xmlparsing import XMLParser

# Given an XML file and a file with a JSON structure, find out which paths in the XML are found in the JSON.
# This is a very loose approach, and will only be used as analysis tool.

def getXMLFiles(startpath):
    files = []
    for p in pathlib.Path(startpath).iterdir():
        if p.is_file() and str(p).lower().endswith('.xml'):
            files.append(str(p))
    return files

def convert(name):
    return name.rstrip().lower().replace('_', '').replace('-', '').replace('/', '')

    
if __name__ == "__main__":
    # Args: [1] is the folder containing a number of XML files.
    #       [2] is the file containing the JSON structure.
    xmlfiles = getXMLFiles(sys.argv[1])
    jsonfile = sys.argv[2]
    jt = EUCDMXMLJSONMapperTool()
    jsonobj = jt.readJSON(jsonfile)
        
    # Go through the xml files:
    for file in xmlfiles:
        xmlparser = XMLParser(file)
        print(file)
        # Get all xpaths for current file:
        xpathlist = xmlparser.getAllPaths()
        
        # Now check each element of the xpath, 
        # to see if it is in the JSON structure.
        for xpath in xpathlist:
            path = xpath.split('/')

            # Just testing how this helps. Normally the root is called CC515C or similar.
            path[0] = 'Declaration'
            
            result = jt.findAnypath(jsonobj, path)
            if result is None:
                print('  Not found.', xpath)
            else:
                print('  Found.', xpath)