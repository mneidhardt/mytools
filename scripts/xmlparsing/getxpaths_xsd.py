import xml.etree.ElementTree as etree
import sys
import os
import re
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.xml.xmlparsing import XMLParser
#--------------------------------------------------------------------------------------------------

###############################

# Traverse an XML structure and print out all XPaths.
#
# Takes 1 arg, the filename of the XML file.
#

xmlfile = sys.argv[1]

xp = XMLParser(xmlfile)
xpaths = xp.getAllPaths_xsd()
for xpath in xpaths:
    print(xpath)
