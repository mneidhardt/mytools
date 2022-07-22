
class Neo4jNode:
    def __init__(self, name, id):
        self.name = name                # The name of this node. String.
        self.id = id                    # The ID of the node (e.g. DENumber in EUCDM). String.

    def getName(self):
        return self.name
        
    def getID(self):
        return self.id
     
    def getCardinality(self):
        return self.cardinality

    def toString(self, var=''):
        return "(" + var + ":Node {name: '" + self.name + "', DENo: '" + self.id + "'})"

class Neo4jChildofRelation:
    def __init__(self, cardinality):
        self.cardinality = cardinality  # Child cardinality wrt. parent. For now its just an integer.

    def getCardinality(self):
        return self.cardinality
                
    def toString(self):
        return "-[:CHILD_OF {cardinality: " + str(self.cardinality) + "}]->"
        