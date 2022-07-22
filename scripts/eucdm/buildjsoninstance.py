import sys
import datetime
import io
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode, Graph
from mytools.eucdm.basestructures import BaseStructures
from mytools.json.jsontools import EUCDMJSONTool
from mytools.eucdm.patternmatcher import PatternMatcher

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
    txt.append('  cn is the columnname you want an instance for. Currently one of these:')
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
    
        sgraf = bs.readSerialisedGraph(filename)
        dedict = bs.getDEDict(defilename)
        graf = gtool.deserialiseGraph(sgraf['nodes'], sgraf['cardinalities'])
        annotateNodes(graf, dedict, jtool)
        gtool.showGraph(graf)
        instance = {}
        instance[jtool.convertName(graf.getName())] = jtool.buildJSONInstance(graf)

        instancefilename = columnname + '.instance.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.json'
        with io.open(instancefilename, 'w', encoding='utf8') as fh:
            fh.write(jtool.dumps(instance))

    except (IndexError, ValueError, NameError) as err:
        print('Error:', err)
        print(syntax(','.join(legalcolumns)))
