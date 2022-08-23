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
# Main difference is that this node can hold a dict of attributes,
# and an origin. 
# Attributes are like ones in XML.
# Origin can hold the origin(s) of the element, these nodes are merged from 
# several XML files, so there can be several origin files for a merged node.
    def __init__(self, name):
        self.attributes = {}
        self.origins = {}
        super().__init__(name)

    def getAttributes(self):
        return self.attributes

    def addAttribute(self, attributename, attributevalue):
        self.attributes[attributename] = attributevalue
    
    def getOrigins(self):
        return list(self.origins)

    def addOrigin(self, origin):
        self.origins[origin] = True
    

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
    # nodes is a list of tuples, as produced by readSerialisedGraph below here.
    # Each node has 3 elements, node key, minimum cardinality and maximum cardinality.
    # At the moment, I do not use minimum cardinality, only maximum cardinality.
    def deserialiseGraph(self, nodes):
        idx = 0
        root = EUCDMNode(nodes[idx][0], nodes[idx][2], None, None)
        self.deserialise(nodes, idx+1, root)
        return root
    
    def deserialise(self, nodes, idx, node):
        if idx >= len(nodes):
            return
        elif nodes[idx][0] == '!':
            self.deserialise(nodes, idx+1, node.getParent())
        else:
            child = EUCDMNode(nodes[idx][0], nodes[idx][2], None, None)
            node.addChild(child)
            child.setParent(node)
            self.deserialise(nodes, idx+1, child)

    # Reads a serialised n-ary tree graph.
    # Returns a list of 3-tuples, one for each node and end-of-child-marker.
    # The 3 elements in a tuple are node key, minimum cardinality, maximum cardinality.
    #
    # Expects a serialisation using end-of-child-marker.
    # A serialised graph must have 3 pieces of information per line, separated by a slash.
    # The 3 pieces are the node key and its min. and max. cardinality.
    # As an example 7/1/9 means node key is 7, with min. cardinality 1 and max. cardinality 9.
    # As end-of-child marker I use exclamation mark. When one is encountered,
    # it means go up one level.
    # As an example, the serialised graph (imagine that commas are replaced with newlines ;):
    # 1,12,01,!,02,!,!,7/9,12,01,!,02,!,03
    # deserialises to this graph:
    #        1
    #       / \
    #    12    7
    #   / \     \
    # 01  02     12
    #          /  |  \
    #         01  02  03
    # The node labelled 7 has cardinality of 9, though this is not shown in the graph.
    # This is used in JSON Schema.
    #
    # This is based on a version from class BaseStructures. I think its better placed here.
    # Also, this version can read a serialised graph with both minimum and maximum cardinality
    # for a node. I have made this backwards compatible, so this reads files where a line
    # has either 1, 2 or 3 pieces of information.
    # If only the node key is present, min. and max. cardinality are set to 1.
    # If only the node key and 1 cardinality number are present, min. cardinality is set to 1,
    # and max. cardinality is set to the value from the file.
    # If the node key and 2 values are present, they are interpreted as node key, min. cardinality
    # and max. cardinality.
    #-------------------------------------------------------------------------------------------
    def readSerialisedGraph(self, filename):
        nodes = []

        with open(filename) as f:
            lineno=0
            for line in f:
                lineno += 1
                line = line.strip()
                if line.lstrip().startswith('#'):
                    continue
                elems = [e.strip() for e in line.split('/')]

                if len(elems) == 3:
                    tuple = (elems[0], int(elems[1]), int(elems[2]))
                elif len(elems) == 2:
                    tuple = elems[0], 1, int(elems[1])
                elif len(elems) == 1 and elems[0] == '!':
                    tuple = '!', 0, 0
                elif len(elems) == 1:
                    tuple = elems[0], 1, 1
                else:
                    raise ValueError('Something is not right on line ' + str(lineno))
                
                nodes.append(tuple)

        return nodes

