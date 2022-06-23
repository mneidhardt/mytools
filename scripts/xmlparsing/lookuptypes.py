import sys
import csv
import re
import xml.etree.ElementTree as etree

#
# Given 1 CSV file with type information and an XSD file,
# the type information in the CSV file is looked up in the XSD and the underlying basic types are added.
# This was originally made to work on output from getxpaths_xsd.py.
#
# Args.
#   CSV file
#   XSD file
#   ColumnID (the column in the CSV file where the type info is. Zero based!

def readCSVFile(filename):
    result = []

    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            result.append(row)

    return result

# Remove NS string.
def cleanupTag(tag):
    NSpattern = re.compile('^\{[^}]+\}(.+)$')
    match = NSpattern.match(tag)
    if match:
        return match.group(1)
    else:
        return tag

def getRestrictions(NS, node):
    restrictions = []
    
    if node is None:
        return restrictions

    for child in node:
        if child.tag == NS+'restriction':
            restrictions.append('base:' + child.attrib['base'])
            restrictions.extend(getRestrictions(NS, child))
        elif child.tag in [NS+'minLength', NS+'maxLength', NS+'pattern']:
            restrictions.append(cleanupTag(child.tag)+':' + child.attrib['value'])
    return restrictions
    
# Search XSD file for a given type name.
# Should I check for duplicate definitions?
# I use find i.s.o. findall, because the return value suits me:
# When iterating over this result, I get the children of the found node, where as
# iterating over the result of findall first goes through the found node itself.
def search4type(NS, xsdroot, typename):
    res = xsdroot.find(NS + 'complexType[@name="' + typename + '"]')
    if res is not None:
        return res
    res = xsdroot.find(NS + 'simpleType[@name="' + typename + '"]')
    if res is not None:
        return res

    return None

csvfile = sys.argv[1]
xsdfile = sys.argv[2]
columnid = int(sys.argv[3])
NS = '{http://www.w3.org/2001/XMLSchema}'

xsdroot = etree.parse(xsdfile).getroot()
csv = readCSVFile(csvfile)


for row in csv:
    if row[0] == 'RAAISW01/Header/DateTimeIssue':
        verbose = False
    else:
        verbose = False
        
    if len(row) > columnid and len(row[columnid]) > 0:
        if row[columnid].startswith('xs:'):     # These are standard types.
            restrictions = row[columnid]        # Just use them as-is.
        else:
            typenode = search4type(NS, xsdroot, row[columnid])
            if typenode is None:
                # Homemade search for type info.
                # Remove namespace
                # Split on any whitespace. Input has type followed possibly by space and a value, e.g.:
                # base_iv:Alphanumeric_Max15 [1-9][0-9][0-9][0-9](([0][1|3...
                # This is output that is generated in getxpaths_xsd.
                parts1 = row[columnid].split(':')
                parts2 = parts1[1].split(' ')
                if verbose:
                    print('>>> Search for type ', parts2[0], ' for ', row)
                typenode = search4type(NS, xsdroot, parts2[0])
             
            restrictions = getRestrictions(NS, typenode)
            
        print(';'.join(row), ';', restrictions)
    else:
        print(';'.join(row))