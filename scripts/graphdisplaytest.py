import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode, Graph

# The purpose of this is to see if I can modify the graph while traversing it.
# The modifications consist of deleting leaves (or children) only.
if __name__ == "__main__":

    filename = sys.argv[1] # Name of file containing serialised graph.
    gtool = Graph()
    sgraf = gtool.readSerialisedGraph(filename)
    graf = gtool.deserialiseGraph(sgraf)
    gtool.showGraph(graf)
