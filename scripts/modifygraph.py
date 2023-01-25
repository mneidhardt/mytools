import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode, Graph

def annotateNodes(nodes):
    enrichednodes = []
        
    for node in nodes:
        if node[0] == '!':
            enrichednodes.append(node[0])
        else:
            enrichednodes.append(EUCDMNode(int(node[0]), ' ', node[1], node[2], ' ', ' '))
    return enrichednodes

def showit(node, indent=''):
    if node.getMaxCardinality() > 1:
        hoo = 'WoW!'
    else:
        hoo = ''

    print(indent, node.getKey(), str(node.getMinCardinality()) + '/' + str(node.getMaxCardinality()), hoo)
    
    for kid in node.getChildren():
        showit(kid, indent+'    ')

def filter(node):
    # print(node.getKey())
    for i in range(0, len(node.getChildren())):
        if node.getChildren()[i].getMaxCardinality() > 1 and len(node.getChildren()[i].getChildren()) == 0:
            node.removeChild(i)
        else:
            filter(node.getChildren()[i])

if __name__ == "__main__":

    filename = sys.argv[1] # Name of file containing serialised graph.
    gtool = Graph()
    nodes = gtool.readSerialisedGraph(filename)
    graf = gtool.deserialiseGraphLoop(annotateNodes(nodes))
    showit(graf)
    filter(graf)
    print('------- filtering----------')
    showit(graf)
    sg = gtool.serialiseGraph(graf)
    print(sg)