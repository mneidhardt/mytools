import json
import sys
import re
import csv
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import Neo4jNode

# Class that reads a JSON document and produces a serialised graph of it.
class JSON2Graf():
    # Args:
    # filename is the name of the JSON Schema file.
    # refname is the name used as root key for the elements that make up the definitions.
    # I.e. the ones that you can refer to using $ref.
    # Leave empty if your schema does not use $ref.
    def __init__(self, filename):
        self.filename = filename
        self.js = self.readJSON(filename)
        
    def readJSON(self, filename):
        with open(filename) as f:
            return json.load(f)
            
        
    # The method that converts JSON to a graph of nodeclass nodes.
    # startkey is the name of the key to use as starting point.
    # This enables me to create a graph of only a subtree, if wanted.
    def dfs(self, startkey):
        result = []
        for key in self.js:
            if key.startswith(startkey):
                result.append(key)
                self._dfs(self.js[key], result)
        return result

    def _dfs(self, node, result):
        if isinstance(node, dict) and len(node) == 0:
            result.append('!')
        elif isinstance(node, dict):
            for key in node:
                result.append(key)
                self._dfs(node[key], result)
            result.append('!')
        elif isinstance(node, list):
            print('Got an array:', node)    # There should be no arrays here, so this is not expected to happen!
            for elm in node:
                if isinstance(elm, str) or isinstance(elm, number):
                    pass
                    #print(indent, elm)
                else:
                    self._dfs(elm, result)
        else:
            result.append('!')

class Lookup():
    def readCSVFile(self, filename):
        result = []

        with open(filename) as csvfile:
            crdr = csv.reader(csvfile, delimiter=';')
            for row in crdr:
                result.append(row)

        return result

    def writeCSVFile(self, csvdata, filename):
        with open(filename, 'w', newline='') as csvfile:
            mywriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='|')
            for row in csvdata:
                mywriter.writerow(row)

    # In this version of the input, the key can contain the following:
    # name, description, mincard, maxcard.
    # Furthermore, description can contain this:
    #   DENumber
    #   DENumber;DDN[XT]A
    #   DDN[XT]A
    def decodeString(self, text):
        parts = text.split('>')
        return parts
    
    def lookupNumber(self, table, columnid, string):
        for row in table:
            if row[columnid] == string:
                return row[0]
        return None

    def lookupString(self, table, columnid, string):
        result = []
        for row in table:
            s1 = row[columnid].lower().strip().replace(' ', '').replace('_', '').replace('-', '')
            if s1 == string.lower():
                result.append(row[0])
        return result

if __name__ == "__main__":
    filename = sys.argv[1]
    datacatalogfile = sys.argv[2]
    
    jg = JSON2Graf(filename)

    # First, create a serialised graph of the JSON input:
    result = jg.dfs('Declaration')
    
    # Second, the names need processing.
    # They come from the schema, and contain a combination of name, description (which often contains DENumber and sometimes DDNXA or DDNTA),
    # and min and max cardinality.
    lu = Lookup()
    
    csvdata = lu.readCSVFile(datacatalogfile)

    denopattern = re.compile('^\d\d\s+\d\d\s+\d\d\d\s+\d\d\d$')
    ddnpattern = re.compile('^DDN[XT]A$', re.IGNORECASE)
    bothpattern = re.compile('^\d\d\s+\d\d\s+\d\d\d\s+\d\d\d[ ;]+DDN[XT]A$', re.IGNORECASE)

    for line in result:
        if line.strip() == '!':
            print('!')
        else:
            parts = lu.decodeString(line)
            if denopattern.match(parts[1]):
                pk = lu.lookupNumber(csvdata, 1, parts[1])
                if pk is not None:
                    print(pk + '/' + parts[2] + '/' + parts[3])
                else:
                    print('?0', parts[0], parts[1])
            elif ddnpattern.match(parts[1]):
                pk = lu.lookupString(csvdata, 5, parts[0])
                if len(pk) == 1:
                    print(pk[0] + '/' + parts[2] + '/' + parts[3])
                elif len(pk) > 1:
                    print('?A1', '>'.join(parts), 'PKs=', '+'.join(pk))
                else:
                    print('?A2', '>'.join(parts))
            elif ';' in parts[1]:
                p2 = parts[1].split(';')
                if denopattern.match(p2[0]):
                    pk = lu.lookupNumber(csvdata, 1, p2[0])
                    if pk is not None:
                        print(pk + '/' + parts[2] + '/' + parts[3])
                    else:
                        print('?B2', '>'.join(parts))
                else:
                    print('?C', '>'.join(parts))
            else:
                pk = lu.lookupString(csvdata, 5, parts[0])
                if len(pk) == 1:
                    print(pk[0] + '/' + parts[2] + '/' + parts[3])
                elif len(pk) > 1:
                    print('?E', '>'.join(parts), 'PKs=', '+'.join(pk))
                else:
                    print('?D', '>'.join(parts))
            