import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.xml.xsdparsing import XSDParser
#--------------------------------------------------------------------------------------------------

# Parse XSD and produce an XML structure accordingly, including restrictions and cardinalities.
#

xp = XSDParser(sys.argv[1])
xp.findNS()
