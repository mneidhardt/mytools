import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.xml.xmltools import XMLTools

    
xt = XMLTools()

filenames = xt.getFilesByType(sys.argv[1], '.xsd')
lines = []
for file in filenames:
    lines.extend(xt.readFilelines(file))

#print('Got lines: ', len(lines))
#sys.exit(0)

minvalues = xt.readCardinalities(lines, 'min')
maxvalues = xt.readCardinalities(lines, 'max')

# Now merge the keys from minvalues and maxvalues.
both = list(minvalues)
both.extend(list(maxvalues))

for element in sorted(both, key=str.lower):
    minval = None
    maxval = None
    
    if element in minvalues:
        minval = min(minvalues[element])
    else:
        minval = 1
    if element in maxvalues:
        maxval = max(maxvalues[element])
    else:
        maxval = 1
    print(element, ';', minval, ';', maxval)
    