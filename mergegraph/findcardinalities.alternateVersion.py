import sys
import re
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.files.filetools import FileTools

# Checking if the cardinalities are OK.
# For incorporating DDNXA/DDNTA into our schema, I read the cardinalities by just finding
# all occurrences of <xs:element ..> in all XSDs, see findcardinalities.py.
# This is an attempt to verify that.
# I used fgrep to get all lines with minoccurs and maxoccurs from the XSD files, stored in a file.
# Like so:
#
#    fgrep -i minoccurs 5.15.0-v0.10-SfR/DDNXA_APP_X_5.15.0-v0.10-SfR/*.xsd > allMinOccurs_fromXSD.txt
#    fgrep -i maxoccurs 5.15.0-v0.10-SfR/DDNXA_APP_X_5.15.0-v0.10-SfR/*.xsd >> allMinOccurs_fromXSD.txt
#
# This script will consolidate lines in that file into a dict:
#   key = element name, value = [minOccurs, maxOccurs].
# Since there are duplicates of element names, I consolidate by taking the smallest version of minOccurs
# and the largest version of maxOccurs for each element.
#

# Input file is made as described above, with fgrep. It contains 1 or more <xs:element...> on each line,
# and either minOccurs, maxOccurs or both as attributes to this element.
filename = sys.argv[1]

def addToDict(result, name, minoccurs, maxoccurs):
    if name in result:
        result[name][0] = min(result[name][0], minoccurs)
        result[name][1] = max(result[name][1], maxoccurs)
    else:
        result[name] = []
        result[name].append(minoccurs)
        result[name].append(maxoccurs)

ft = FileTools()

lines = ft.readFilelines(filename)

result = {}
p0 = re.compile('\s*(<xs:element [^>]+>)\s*', re.IGNORECASE)
p1 = re.compile('.*name="([^"]+)".*', re.IGNORECASE)
p2 = re.compile('.*minOccurs="(\d+)".*', re.IGNORECASE)
p3 = re.compile('.*maxOccurs="(\d+)".*', re.IGNORECASE)

for line in lines:
    line = line.strip()
    m0 = p0.findall(line)
    for hit in m0:
        m1 = p1.match(hit)
        m2 = p2.match(hit)
        m3 = p3.match(hit)
        
        if m1 and m2 and m3:
            addToDict(result, m1.group(1), int(m2.group(1)), int(m3.group(1)))
        elif m1 and m2:
            addToDict(result, m1.group(1), int(m2.group(1)), 1)
        elif m1 and m3:
            addToDict(result, m1.group(1), 1, int(m3.group(1)))
        elif m1:
            print('missing min and max!')
        else:
            print('No name.')

for key in result:
    print(key, ';', result[key][0], ';', result[key][1])