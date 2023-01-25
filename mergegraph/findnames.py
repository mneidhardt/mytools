import sys
import datetime
import io
import pathlib
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.json.jsontools import JSONTool
from mytools.xml.xmlparsing import XMLParser

# Given a number of XML files and a file with a JSON structure, this searches the 
# JSON keys for every element name in the XML files.
# I.e., I want to see which of the XML leaves are found as a JSON key.
# This only concerns itself with names of individual elemets, i.e.
# it doesnt try to find full paths.

def getXMLFiles(startpath):
    files = []
    for p in pathlib.Path(startpath).iterdir():
        if p.is_file() and str(p).lower().endswith('.xml'):
            files.append(str(p))
    return files

def convert(name):
    return name.rstrip().lower().replace('_', '').replace('-', '').replace('/', '')

def checkNames(list, jsonkeys, result):
    for e in list:
        e2 = convert(e)
        # The converted name is either:
        # a) in the JSON and already seen, or
        # b) in the JSON and not yet seen, or
        # c) not in the JSON. If not seen yet, add it to result with a 0 as valude
        if e2 in jsonkeys and e2 in result:
            result[e2] += 1
        elif e2 in jsonkeys:
            result[e2] = 1
        else:
            if e2 not in result:
                result[e2] = 0
    
if __name__ == "__main__":
    # Args: [1] is the folder containing a number of XML files.
    #       [2] is the file containing the JSON structure.
    xmlfiles = getXMLFiles(sys.argv[1])
    jsonfile = sys.argv[2]
    jt = JSONTool()
    jsonobj = jt.readJSON(jsonfile)
    jsonkeys = []
    key2denumber = {}
    for k in set(jt.allKeys(jsonobj)):
        jsonkeys.append(convert(k))
        denumbers = []
        elements = jt.findElement(jsonobj, k) # Find DENumber of this key.
        for e in elements:
            if 'description' in e:
                denumbers.append(e['description'])
        key2denumber[convert(k)] = denumbers

    result = {}
        
    # Go through the xml files:
    for file in xmlfiles:
        xmlparser = XMLParser(file)

        # Get all xpaths for current file:
        xpathlist = xmlparser.getAllPaths()
        
        # Now check each element of the xpath, 
        # to see if it is in the JSON structure.
        for xpath in xpathlist:
            path = xpath.split('/')
            checkNames(path, jsonkeys, result)            

    for w in sorted(list(result)):
        if result[w] >= 1:
            print(w, result[w], 'DENumbers: ', ','.join(key2denumber[w]))
            
    for w in sorted(list(result)):
        if result[w] == 0:
            print(w, result[w])
            
