import io
import re
import pathlib

class XMLTools():

    # Get a list of files in a given directory, whose names end with the given string.
    def getFilesByType(self, startpath, filenameEndsWith):
        files = []
        for p in pathlib.Path(startpath).iterdir():
            if p.is_file() and str(p).lower().endswith(filenameEndsWith.lower()):
                files.append(str(p))
        return files

    # Read a file line by line.
    def readFilelines(self, filename):
        result = []
        with open(filename) as f:
            for line in f:
                result.append(line)
        return result
        
    # Read a file with element names and accompanying maxOccurs.
    # Given a list of lines, from an XSD, containing XML element definitions,
    # this will find cardinality info.
    # Args:
    #   list: a list of element definition straight from an XSD, e.g. <xs:element name="blabla" minOccors="0" maxOccurs="3"...>
    #   minmax is 'min' for minOccurs, 'max' for maxOccurs.
    # Returns a dict with key = elementname and value = a set of all min/maxOccurs for elementname.
    def readCardinalities(self, list, minmax):
        result = {}
        p0 = re.compile('(<xs:element [^>]+>)', re.IGNORECASE)
        p1 = re.compile('.*name="([^"]+)".*', re.IGNORECASE)
        if minmax == 'min':
            p2 = re.compile('.*minOccurs="(\d+)".*', re.IGNORECASE)
        elif minmax == 'max':
            p2 = re.compile('.*maxOccurs="(\d+)".*', re.IGNORECASE)
        else:
            print('minmax arg not recognised: ', minmax)
            return None

        for line in list:
            # If this is a match, we have one or more elements that we can analyse for min/maxoccurs.
            # There may be more than one element on a line.
            m0 = p0.findall(line)
            
            # Now check each of the elements found (if any):
            for hit in m0:
                m1 = p1.match(hit)
                m2 = p2.match(hit)
                if m1 and m2:
                    elementname = m1.group(1)
                    occurs = int(m2.group(1))
                    if elementname not in result:
                        result[elementname] = set()
                    result[elementname].add(occurs)

        return result
