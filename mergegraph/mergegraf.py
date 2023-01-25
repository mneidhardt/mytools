import sys
import datetime
import io
import pathlib
import re
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import GraphmergeNode, Graph
from mytools.xml.xmltools import XMLTools
from mytools.xml.xmlparsing import XMLParser
from mytools.xml.xmlbuilding import XMLBuilder

# This script will merge a number of XML files into one.
# It was made in order to merge the files from DDNXA used between DMS and KRIA,
# 14 XSDs in all. These XSDs were converted to XML samples with XMLSpy, and the resulting
# XML files are used for input here.

# Read CSV file with cardinalities. This must not contain duplicates.
# Returns a dict with XML element name as key, 
# and a list with 2 elements, minOccurs and maxOccurs, as value.
def readCardinalities(filename):
    result = {}
    
    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            if len(row) == 3:   # or row[0].lstrip().startswith('#'):
                result[row[0].strip()] = [row[1].strip(), row[2].strip()]

    return result

# Read a file with element names and accompanying maxOccurs.
# Returns a dict with key = elementname and value = maxOccurs.
def readMaxoccurs(filename):
    result = {}
    p1 = re.compile('.*name="([^"]+)".*', re.IGNORECASE)
    p2 = re.compile('.*maxOccurs="(\d+)".*', re.IGNORECASE)
    with open(filename) as f:
        for line in f:
            m1 = p1.match(line)
            m2 = p2.match(line)
            if m1 and m2:
                result[m1.group(1)] = m2.group(1)
            else:
                print('NB: No maxoccurs match on this line: ', line.strip())

    return result

def makeGraph(node, path, origin):
    if len(path) == 0:
        return
    else:
        if len(node.getChildren()) == 0:
            child = GraphmergeNode(path[0])
            node.addChild(child)
            child.setParent(node)
            child.addOrigin(origin)
            if path[0] in cardinalities:
                child.addAttribute('minOccurs', cardinalities[path[0]][0])
                child.addAttribute('maxOccurs', cardinalities[path[0]][1])
            makeGraph(child, path[1:], origin)
        else:
            # Here are 2 cases: Either path[0] is found among the kids or not.
            # If found, continue with next name in path, i.e. do recursive call.
            # If not, a child is added to node.
            found = False
            for kid in node.getChildren():
                if path[0].lower() == kid.getName().lower():
                    kid.addOrigin(origin)
                    if path[0] in cardinalities:
                        kid.addAttribute('minOccurs', cardinalities[path[0]][0])
                        kid.addAttribute('maxOccurs', cardinalities[path[0]][1])
                        # kid.addAttribute('maxOccurs', maxoccurs[path[0]])
                    makeGraph(kid, path[1:], origin)
                    found = True

            if not found:
                child = GraphmergeNode(path[0])
                node.addChild(child)
                child.setParent(node)
                child.addOrigin(origin)
                if path[0] in cardinalities:
                    child.addAttribute('minOccurs', cardinalities[path[0]][0])
                    child.addAttribute('maxOccurs', cardinalities[path[0]][1])
                    # child.addAttribute('maxOccurs', maxoccurs[path[0]])
                makeGraph(child, path[1:], origin)

if __name__ == "__main__":
    # Args: 
    xmldir = sys.argv[1]            # The dir where the xml files are.
    cardinalityfile = sys.argv[2]   # The file holding the element names and corresponding cardinalities. This is a csv file with 3 fields per line: element-name; minOccurs; maxOccurs.
                                    # This can be -, meaning no cardinalities to read.
    output = sys.argv[3]            # The type of output wanted. Either csv or xml.

    xt = XMLTools()
    
    files = xt.getFilesByType(xmldir, '.xml')
    
    if cardinalityfile == '-':
        print('Skipping cardinality file')
        cardinalities = {}
    else:
        print('Using cardinality file.')
        cardinalities = readCardinalities(cardinalityfile)

    commonrootname = 'ROOT'
    root = GraphmergeNode(commonrootname)

    # Go through the xml files to merge:
    for file in files:
        xmlparser = XMLParser(file)

        # Set the name of root in the merged graph:
        oldrootname = xmlparser.setRootname(commonrootname)

        # Get all xpaths for current file:
        xpathlist = xmlparser.getAllPaths()
        
        for xpath in xpathlist:
            path = xpath.split('/')
            path.pop(0) # Drop the root, it is already present in new graph.
            makeGraph(root, path, oldrootname)
        
    if output == 'csv':
        g = Graph()
        g.showMergedGraph(root)
    elif output == 'xml':
        # If you want to show to merged graph as XML, with attributes as text, use this:
        xmlbuilder = XMLBuilder(commonrootname)
        xmlbuilder.buildXML(root, xmlbuilder.getNewXML())
        xmlfilename = xmlbuilder.writeXML('mergedgraph')
        print('Wrote xml to file: ', xmlfilename)
    else:
        print(output, 'not recognised. Use either csv or xml.')
