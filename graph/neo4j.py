import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import Node

class Neo4jNode(Node):
    def __init__(self, name, id, mincard=None, maxcard=None):
        super().__init__(name)          # The name of this node. String.
        self.id = id                    # The ID of the node (e.g. DENumber in EUCDM). String.
        self.mincardinality = int(mincard)   # Minimum cardinality for this node in relation to its parent. Integer.
        if maxcard is None:             # Maximum cardinality for this node in relation to its parent. Integer.
            self.maxcardinality = int(mincard)
        else:
            self.maxcardinality = int(maxcard)

    def getID(self):
        return self.id

    def getMinCardinality(self):
        return self.mincardinality
     
    def getMaxCardinality(self):
        return self.maxcardinality
    
    # Stringify node, possibly with relation.
    # Made for use with depth first search of a graph, e.g. XSD or JSON Schema.
    # 
    def toString(self):
        rel = self.relationToString()
        node = "(:Node {name: '" + self.name + "', DENo: '" + self.id + "'})"
        if self.parent is None:
            return node
        else:
            return self.relationToString() + node
            
    def relationToString(self, direction='L'):
        relation = "-[:CHILD_OF {mincardinality: " + str(self.getMinCardinality()) + ", maxcardinality: " + str(self.getMaxCardinality()) + "}]-"
        if direction.upper() == "L":
            return "<" + relation
        else:
            return relation + ">"
