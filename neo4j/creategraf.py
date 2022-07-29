import re
import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.neo4j import Neo4jNode
import xml.etree.ElementTree as etree
from neo4jwriter import Neo4JWriter

class Neo4JImport:
    def __init__(self):
        self.id = 0
        self.NSpattern = re.compile('^\{[^}]+\}(.+)$')

    def connect(self, userid, password):
        bolt_url = 'bolt://localhost:7687'
        Neo4JWriter.enable_log()
        return Neo4JWriter(bolt_url, userid, password)

    def getNextID(self):
        self.id += 1
        return self.id
        
    def cleanupTag(self, tag):
        match = self.NSpattern.match(tag)
        if match:
            return match.group(1)
        else:
            return tag

    # Convert an XML node from ElementTree to a Neo4jNode.
    def convertEtreeNode(self, etreenode):
        minoccurs = 1
        maxoccurs = 1
        if 'minOccurs' in etreenode.attrib:
            minoccurs = int(etreenode.attrib['minOccurs'])
        if 'maxOccurs' in etreenode.attrib:
            if etreenode.attrib['maxOccurs'].lower() == 'unbounded':
                maxoccurs = 99999
            else:
                maxoccurs = int(etreenode.attrib['maxOccurs'])
            
        return Neo4jNode(self.cleanupTag(etreenode.tag), str(etreenode.attrib['id']), minoccurs, maxoccurs)

    # Insert an XML instance file into Neo4j.
    # Arg when calling is the root of the XML tree.
    # The method keeps the path from the root to the parent of the current node at all times.
    # I then match this path and merge the current node as a child of the last node in the matched path.
    # I.e. varname is only used in the last node in the path, i.e. the parent of the current node.
    def dfs4Neo(self, node, path=[]):
        result = []
        varname = 'a'
        
     
        neo4jnode = self.convertEtreeNode(node)
        
        if len(path) > 0:
            matchcmd = []
            # For inserting a node, I first match its path all the way from immediate parent up to the root,
            # and then merge the current node in a relation to its immediate parent.
            # We start from scratch so first node is also just a CREATE.
            # The following commands are all MATCH+MERGE.
            # E.g.:
            # Match (:Node {name: 'N1'})<-[:CHILD_OF]-(a:Node {name: 'N2'})
            # Merge (a)<-[:CHILD_OF]-(:Node {name: 'N3'})
            # The immediate parent therefore needs a variable (varname), so the last node needs to have a variable. 
            # If i==0 and len(path)==1, no relations in path, but it needs varname.
            # Else if i==0, no relation and no varname needed.
            # Else if this is last element in path, it needs a varname.
            # Else this consists of a node with a relation, and no varname.
            for i in range(0, len(path)):
                if i == 0 and len(path) == 1:
                    matchcmd.append(path[i].toString(varname))
                elif i == 0:
                    matchcmd.append(path[i].toString())
                elif i == len(path)-1:
                    matchcmd.append(path[i].toStringWithRelation(varname))
                else:
                    matchcmd.append(path[i].toStringWithRelation())
                    
            result.append('MATCH ' + ''.join(matchcmd) + ' MERGE (a)' + neo4jnode.toStringWithRelation() + ';')
        else:
            result.append('CREATE ' + neo4jnode.toString() + ';')

        for child in node:
            result.extend(self.dfs4Neo(child, path + [neo4jnode]))
                
        return result

if __name__ == "__main__":
    xmlfile = sys.argv[1]
    userid = sys.argv[2]
    password = sys.argv[3]

    root = etree.parse(xmlfile).getroot()
    ni = Neo4JImport()
    nw = ni.connect(userid, password)
    
    commands = ni.dfs4Neo(root)
    for command in commands:
        nw.createStatement(command)
        print(command)

    nw.close()