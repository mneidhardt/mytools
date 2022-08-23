import sys
import datetime
import io
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode, Graph
from mytools.eucdm.basestructures import BaseStructures
from mytools.json.jsontools import EUCDMJSONTool
from mytools.eucdm.patternmatcher import PatternMatcher

def baseSchema(version):
    version = [str(e) for e in version] # Convert version numbers to strings.
    result = {}
    result['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    result['schemaVersion'] = '.'.join(version) # e.g. '2.1.0'
    result['title'] = 'Declaration'
    result['description'] = 'Created ' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    result['type'] = 'object'
    result['additionalProperties'] = False
    result['properties'] = {}
    result['properties']['schemaVersion'] = {}
    result['properties']['schemaVersion']['pattern'] = '^' + version[0] + '[.][0-9]+[.][0-9]+$'
    result['properties']['schemaVersion']['type'] = 'string'
    result['properties']['procedureCategory'] = {}      # The current key for what EUCDM calls 'column'. May be changed to 'column'.
    result['properties']['procedureCategory']['type'] = 'string';
    result['properties']['procedureCategory']['maxLength'] = 3;
    #result['properties']['column']['type'] = 'string'
    #result['properties']['column']['enum'] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'I1', 'I2']

    return result

# This will information to nodes of a graph
def annotateNodes(node, dedict, jt):
    node.setName(dedict[node.getKey()][0])
    node.setFormat(dedict[node.getKey()][1])
    node.setCodelist(dedict[node.getKey()][2])

    for kid in node.getChildren():
        annotateNodes(kid, dedict, jt)

def syntax(legalcolumns):
    txt = []
    txt.append(sys.argv[0] + ' sg de cn')
    txt.append('  sg is the filename containing the serialied graph.')
    txt.append('  de is the filename containing the data elements, their names and formats.')
    txt.append('  cn is the columnname you want a schema for. Currently one of these:')
    txt.append(legalcolumns)
    return "\n".join(txt)

if __name__ == "__main__":

    try:
        legalcolumns = [ 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'I1', 'I2' ]

        filename = sys.argv[1] # Name of file containing serialised graph.
        defilename = sys.argv[2] # Name of file containing data element number, name and format.
        columnname = sys.argv[3] # 'Column' name, currently one of these:
        if columnname not in legalcolumns:
            raise ValueError()

        bs = BaseStructures()
        gtool = Graph()
        jtool = EUCDMJSONTool()
        jtool.setPatternMatcher(PatternMatcher())
    
        sgraf = gtool.readSerialisedGraph(filename)
        dedict = bs.getDEDict(defilename)
        graf = gtool.deserialiseGraph(sgraf)
        annotateNodes(graf, dedict, jtool)
        gtool.showGraph(graf)
        schema = {}
        schema[jtool.convertName(graf.getName())] = jtool.buildJSONSchema(graf)
        version = [2,2,0]
        result = baseSchema(version)
        convertedname = jtool.convertName(graf.getName())   # This is the name of the root node.
        result['properties'][convertedname] = schema[convertedname]
    
        schemafilename = columnname + '.schema.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.json'
        with io.open(schemafilename, 'w', encoding='utf8') as fh:
            fh.write(jtool.dumps(result))

    #except (IndexError, ValueError, NameError):
    except Error as err:
        print(str(err))
        print(syntax(','.join(legalcolumns)))
