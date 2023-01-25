import xml.etree.ElementTree as etree
import sys
import os
import re
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.xml.xmlparsing import XMLParser
#--------------------------------------------------------------------------------------------------

###############################

# Traverse an XML structure and gather all attributes.
# Return the attribs in dict with number of occurrences as value.
#
# Takes 1 arg, the filename of the XML file.
#

xmlfile = sys.argv[1]

xp = XMLParser(xmlfile)
attribs = xp.gatherAllAttribs()
for attrib in sorted(list(attribs)):
    print(attrib, attribs[attrib])
