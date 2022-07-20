import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.xml.xsdparsing import XSDParser
#--------------------------------------------------------------------------------------------------

# Parse XSD and produce an XML structure accordingly, including restrictions and cardinalities.
#

if len(sys.argv) < 2:
    print('Syntax:\n',sys.argv[0],'xsd-filename')
    sys.exit(0)

xp = XSDParser(sys.argv[1])
xp.start()
output = xp.writeXML()
print('Wrote xml to', output)