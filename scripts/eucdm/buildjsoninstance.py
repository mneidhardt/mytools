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

def syntax():
    txt = []
    txt.append(sys.argv[0] + ' sg de cn')
    txt.append('  sg is the filename containing the serialied graph.')
    txt.append('  de is the filename containing the data elements, their names and formats.')
    txt.append('  cn is the columnname you want an instance for. Currently not necessary.')
    return "\n".join(txt)

if __name__ == "__main__":

    try:
        filename = sys.argv[1] # Name of file containing serialised graph.
        defilename = sys.argv[2] # Name of file containing data element number, name and format.
        columnname = sys.argv[3] # 'Column' name, currently only used as part of filename.

        bs = BaseStructures()
        gtool = Graph()
        jtool = EUCDMJSONTool()
        jtool.setPatternMatcher(PatternMatcher())
    
        sgraf = gtool.readSerialisedGraph(filename)
        dedict = bs.getDEDict(defilename)
        graf = gtool.deserialiseGraph(sgraf)
        annotateNodes(graf, dedict, jtool)
        gtool.showGraph(graf)
        instance = {}
        instance[jtool.convertName(graf.getName())] = jtool.buildJSONInstance(graf)

        instancefilename = columnname + '.instance.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.json'
        with io.open(instancefilename, 'w', encoding='utf8') as fh:
            fh.write(jtool.dumps(instance))

    except Exception as err:
        print('Error:', str(err))
        print(syntax())
