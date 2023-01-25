import re
import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.neo4j import Neo4jNode
from mytools.json.jsontools import JSONTool
import csv
from neo4jwriter import Neo4JWriter

class Neo4JImport:
    def __init__(self):
        self.id = 0

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

    # Convert a JSON "node" to a Neo4jNode.
    # In this case, a JSONNode is simply a text string formattet like this:
    # <name>&<DENo;minCard;maxCard>
    def convertJSONNode(self, jsonnode):
        name,rest = jsonnode.split('&')
        description, mincard, maxcard = rest.split(';')

        if 'id' in etreenode.attrib:
            return Neo4jNode(self.cleanupTag(etreenode.tag), str(etreenode.attrib['id']), minoccurs, maxoccurs)
        else:
            return Neo4jNode(self.cleanupTag(etreenode.tag), str(self.getNextID()), minoccurs, maxoccurs)

    def dfs(self, node, indent=''):
        if isinstance(node, dict):
            for key in node:
                print(indent, key)
                self.dfs(node[key], indent+'  ')
        elif isinstance(node, list):
            for elm in node:
                if isinstance(elm, str) or isinstance(elm, number):
                    print(indent, elm)
                else:
                    self.dfs(elm, indent+'  ')
        else:
            print(indent, node)
            
    # Insert a JSON instance file into Neo4j.
    # Arg when calling is the root of the JSON structure.
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
                    
            result.append('MATCH ' + 
                ''.join(matchcmd) + 
                ' MERGE (a)' + 
                neo4jnode.toStringWithRelation() + 
                ';')
        else:
            result.append('CREATE ' + neo4jnode.toString() + ';')

        for child in node:
            result.extend(self.dfs4Neo(child, path + [neo4jnode]))
                
        return result

if __name__ == "__main__":
    jsonfile = sys.argv[1]
    datacatalogfile = sys.argv[2]   # Currently this is a CSV file with 4 columns:
    userid = sys.argv[3]
    password = sys.argv[4]

    ni = Neo4JImport()
    nw = ni.connect(userid, password)
    jt = JSONTool()
    js = jt.readJSON(jsonfile)
    ni.dfs(js)
    
    #commands = ni.dfs4Neo(js)
    #for command in commands:
    #    nw.createStatement(command)
    #    print(command)

    nw.close()