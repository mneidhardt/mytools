import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from xsd2xml.xsdparser import XSDParser
#--------------------------------------------------------------------------------------------------

# Parse XSD and produce an XML structure accordingly, including restrictions and cardinalities.
#

xp = XSDParser(sys.argv[1])
xp.start()
output = xp.writeXML()
print('Wrote xml to', output)