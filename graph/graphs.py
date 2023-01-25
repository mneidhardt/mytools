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

    def removeChild(self, id):
        self.children.pop(id)
        
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
    def __init__(self, key, name, mincardinality, maxcardinality, altkey=None, format=None, codelist=None):
        if not isinstance(key, int):
            raise ValueError('Key must be an integer:', key)
        elif not isinstance(name, str):
            raise ValueError('Name must be a string:', name)
        elif not isinstance(mincardinality, int):
            raise ValueError('Min.cardinality must be an integer:', mincardinality)
        elif not isinstance(maxcardinality, int):
            raise ValueError('Max.cardinality must be an integer:', maxcardinality)
            
        super().__init__(name)
        self.key = key                          # This is the ID of the node in the data catalog. Int.
        self.mincardinality = mincardinality    # Minimum cardinality of this node in relation to its parent. Int.
        self.maxcardinality = maxcardinality    # Maximum cardinality of this node in relation to its parent. Int.
        super().__init__(name)                  # Name of the node. String.
        self.altkey = altkey                    # Alternative key, e.g. DE Number or EUCDM. String.
        self.format = format                    # Format for the node, if relevant (an..XY or similar, as in EUCDM). String.
        self.codelist = codelist                # Boolean stating whether this field has a code list. Value is one of ['Y', 'N', None].
        
    def getKey(self):
        return self.key
     
    def getAltKey(self):
        return self.altkey
     
    def getMinCardinality(self):
        return self.mincardinality

    def getMaxCardinality(self):
        return self.maxcardinality

    def getFormat(self):
        return self.format

    def getCodelist(self):
        return self.codelist

    # Helper method for use mainly when creating a JSON Schema.
    def getDescription(self):
        result = []
        separator = '/'
        replacement = '#' + str(ord(separator)) + ';'
        
        for v in [self.key, self.altkey, self.format]:
            if v is not None:
                result.append(str(v).replace(separator, replacement))
            else:
                result.append('')
        return separator.join(result)
        
    def __repr__(self):
        result = []
        for v in [self.key, self.name, self.mincardinality, self.maxcardinality, self.altkey, self.format, self.codelist]:
            if v:
                result.append(str(v))
            else:
                result.append('None')

        return '; '.join(result)


class Neo4jNode(Node):
    def __init__(self, name, id, ownid=None, mincard=None, maxcard=None):
        super().__init__(name)          # The name of this node. String.
        self.id = id                    # The ID of the node. String.
        self.ownID  = ownid             # If the node has an ID of its own, e.g. DENumber for EUCDM. String.
        self.mincardinality = mincard   # Minimum cardinality for this node in relation to its parent. Integer.
        self.maxcardinality = maxcard   # Maximum cardinality for this node in relation to its parent. Integer.
        self.subschemas = []            # This is a list of the subschemas this node participates in.

    def getID(self):
        return self.id

    def setOwnID(self, ownid):
        self.ownid = ownid

    def getMinCardinality(self):
        return self.mincardinality
     
    def getMaxCardinality(self):
        return self.maxcardinality

    def getSubSchemas(self):
        return self.subschemas

    def addSubSchema(self, subschema):
        self.subschemas.append(subschema)
    
    # Stringify node, possibly with relation.
    def toString(self, varname=''):
        return "(" + varname + ":Node {name: '" + self.name + "', ID: '" + self.id + "'})"
        
    def toStringWithRelation(self, varname='', direction='L'):
        relation = "-[:CHILD_OF {mincardinality: " + str(self.getMinCardinality()) + ", maxcardinality: " + str(self.getMaxCardinality()) + "}]-"
        if direction.upper() == "L":
            return "<" + relation + self.toString(varname)
        else:
            return relation + ">" + self.toString(varname)

class Graph():
    def __init__(self):
        self.count = 0
        self.schema = {}
        
    def showGraph(self, node, indent=''):
        print(indent, str(node))

        if False:
            char = '    '
        elif len(indent) == 0 or indent[-1] == '+':
            char = '----'
        else:
            char = '++++'
            
        for kid in node.getChildren():
            self.showGraph(kid, indent+char)

    def showMergedGraph(self, node, indent=0):
        print(indent*';', str(node))

        for kid in node.getChildren():
            self.showMergedGraph(kid, indent+1)

    # Does depth first traversal, with path.
    # This means that the method saves the full path of every leaf.
    # Returns a list of all leaves with full path.
    def dfswp(self, node, path=[]):
        result = []
        
        if node is None:
            return result
        else:
            path.append(node.getName())

        if len(node.getChildren()) == 0:
            result.append('.'.join(path))
        else:
            for child in node.getChildren():
                result.extend(self.dfswp(child, path))
                path.pop()
        
        return result


    
    # Serialises a graph using end-of-child-markers.
    def serialiseGraph(self, root):
        result = []
        self.serialise(root, result)
        return result
    
    def serialise(self, node, result):
        result.append(node.getKey())
        if len(node.getChildren()) == 0:
            result.append('!')
            return
    
        for kid in node.getChildren():
            self.serialise(kid, result)
        result.append('!')

    def getRoot(self, node):
        while True:
            if node is not None and node.getParent() is not None:
                node = node.getParent()
            else:
                break
        return node

    # The node list, i.e. the argument for deserialiseGraphLoop(), may contain end-of-child-markers at the very end.
    # They have no effect when deserialising a graph, and if there are too many, deserialisation
    # will fail. This will remove them.
    # Of course, you could also ensure that the creator of the serialised graph does not make any errors.
    def removeTrailingMarkers(self, nodes):
        while True:
            if nodes[-1] == '!':
                nodes.pop()
            else:
                break

        return nodes
    
    # Deserialise a graph serialised using end-of-child-markers.
    # This version uses looping, rather than recursion, as recursion only 
    # works with relatively small graphs.
    # One annoying thing with this is that I need to find the root node at the end.
    # This uses EUCDMNode.
    # nodes is a list of either '!' or EUCDMNode, exactly as seen in the serialised graph, but where the real nodes have been 
    # turned into EUCDMNodes.
    def deserialiseGraphLoop(self, nodes):
        nodes = self.removeTrailingMarkers(nodes)
        gnode = nodes[0]
        nodes.pop(0)
        for node in nodes:
            if node == '!':
                gnode = gnode.getParent()
            else:
                gnode.addChild(node)
                node.setParent(gnode)
                gnode = node

        # Since the graph is made using a loop, I need to find the root before I return.
        return self.getRoot(gnode)

    # Recursive version - no good for graphs with more than approx. 900 nodes.
    # Will exceed the max. recursion depth.
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
    # Expects a serialisation made using end-of-child-marker.
    # A serialised graph must have 3 pieces of information per line, separated by a slash.
    # The 3 pieces are the node key and its min. and max. cardinality.
    # As an example 7/0/9 means node key is 7, with min. cardinality 0 and max. cardinality 9.
    # As end-of-child marker I use exclamation mark. When one is encountered,
    # it means go up one level.
    # As an example, the serialised graph (imagine that commas are replaced with newlines ;):
    # 1,12,01,!,02,!,!,7/0/9,12,01,!,02,!,03
    # deserialises to this graph:
    #        1
    #       / \
    #    12    7
    #   / \     \
    # 01  02     12
    #          /  |  \
    #         01  02  03
    # The node labelled 7 has min/max cardinality of 0/9 (though not shown in the graph).
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

    # OBSOLETE!
    # In order to create an overview, this will read a not quite complete, serialised graph.
    # What is missing are keys (into our datacatalog) for the DDNXA and DDNTA fields without
    # DENumber (i.e. almost all of them.
    #-------------------------------------------------------------------------------------------
    def readSemiSerialisedGraph(self, filename):
        nodes = []
        
        raise Exception('Obsolete.')

        with open(filename) as f:
            lineno=0
            for line in f:
                lineno += 1
                line = line.strip()
                if line.lstrip().startswith('#'):
                    continue
                elif line.strip().startswith('?'):
                    elemsB = [e.strip() for e in line.split(' ')]
                    parts = elemsB[1].split('>')
                    elems = [elemsB[0]+parts[0]+parts[1], parts[2], parts[3]]
                else:
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


