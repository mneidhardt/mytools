import json
import sys

class Node():
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []

    def getParent(self):
        return self.parent

    def setParent(self, node):
        self.parent = node

    def getChildren(self):
        return self.children

    def addChild(self, node):
        self.children.append(node)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class GraphmergeNode(Node):
# Started when we did work on merging a number of IExxx messages.
# Main difference is that this node can hold a list of attributes.
# These attributes could be the names of all the original graphs that this node appears in.
    def __init__(self, name):
        self.attributes = {}
        super().__init__(name)

    def getAttributes(self):
        return list(self.attributes)

    def addAttribute(self, attribute):
        self.attributes[attribute] = True

    def __repr__(self):
        return self.name + ';' + ';'.join(self.getAttributes())

# Node class for EUCDM Data Elements. Each such Data Element has a Data Element number,
# called DENumber or DENo. I store this in the field key.
# Cardinality is this node's cardinality in relation to its parent.
# Name is the textual name of the data element.
# Format is the type and size of the field, if any. E.g. an10 for 10 alphanumeric chars,
# and an..30 for 0-30 alphannumeric characters.
#----------------------------------------------------------------------------------------
class EUCDMNode(Node):
    def __init__(self, key, cardinality, name, format):
        super().__init__(name)
        self.key = key              # This is the full DENumber. String.
        self.cardinality = cardinality # Cardinality of this node in relation to its parent. Int.
        self.format = format            # an..XY or similar, as in EUCDM. String.
        self.codelist = None            # Does this field have a code list. Value is one of ['Y', 'N', None].
        
    def getKey(self):
        return self.key
     
    def getDENumber(self):
        return self.denumber

    def getCardinality(self):
        return self.cardinality

    def getFormat(self):
        return self.format

    def setFormat(self, format):
        self.format = format

    def getCodelist(self):
        return self.codelist

    def setCodelist(self, value):
        self.codelist = value

    def __repr__(self):
        result = []
        for v in [self.key, str(self.cardinality), self.name, self.format, self.codelist]:
            if v:
                result.append(v)

        return '; '.join(result)

class Graph():
    def __init__(self):
        self.count = 0
        self.schema = {}
        
    def showGraph(self, node, indent=''):
        print(indent, str(node))

        for kid in node.getChildren():
            self.showGraph(kid, indent+'    ')

    def showMergedGraph(self, node, indent=0):
        print(indent*';', str(node))

        for kid in node.getChildren():
            self.showMergedGraph(kid, indent+1)

    # Serialises a graph using end-of-child-markers.
    def serialiseGraph(self, root):
        result = []
        serialise(root, result)
        return result
    
    def serialise(self, node, result):
        result.append(node.getKey())
        if len(node.getChildren()) == 0:
            result.append('!')
            return
    
        for kid in node.getChildren():
            serialise(kid, result)
        result.append('!')
    
    # Deserialise a graph serialised using end-of-child-markers.
    # This uses EUCDMNode.
    def deserialiseGraph(self, nodes, cardinalities):
        idx = 0
        root = EUCDMNode(nodes[idx], cardinalities[idx], None, None)
        self.deserialise(nodes, cardinalities, idx+1, root)
        return root
    
    def deserialise(self, nodes, cardinalities, idx, node):
        if idx >= len(nodes):
            return
        elif nodes[idx] == '!':
            self.deserialise(nodes, cardinalities, idx+1, node.getParent())
        else:
            child = EUCDMNode(nodes[idx], cardinalities[idx], None, None)
            node.addChild(child)
            child.setParent(node)
            self.deserialise(nodes, cardinalities, idx+1, child)

