import sys
from neo4j import GraphDatabase

# Serialise a Neo4j tree graph.
# This uses relationships, as that is where the cardinality is stored.
#-----------------------------------------------------------------------

def stringifyNode(node):
    return str(node[0]) + '/' + str(node[1]) + '/' + str(node[2])
    
def serialiseGraph(session, rootdeno):
    return serialise(session, [(rootdeno,1,1)])

# Args: session is the Neo4J session.
# path is the list of nodes for the current path. Each of these nodes is a tuple made up of
# of the node key, the key's mininum cardinality and the key's maximum cardinality.
# Cardinality here means the nodes cardinality with respect to its parent. The root node
# has somewhat arbitrarily been given min/max card 1.
# Invariant: path has at least 1 node. The last element is the latest addition,
# and the one whose children I will search for.
def serialise(session, path):
    result = []
    query = createQuery(path)
    # print(query)
    g = session.read_transaction( lambda tx: tx.run(query,).graph())
    result.append(stringifyNode(path[-1]))
    
    if len(g.relationships) == 0:
        result.append('!')
    else:
        for rel in g.relationships:
            # Q: Should relation attributes be included in the search?
            # print('  DENo:', deno, 'Min/MaxCard:', rel['mincardinality'], rel['maxcardinality'])
            key = rel.start_node['DENo']
            if rel['mincardinality'] != 1:
                mincard = rel['mincardinality']
            else:
                mincard = 1
            if rel['maxcardinality'] != 1:
                maxcard = rel['maxcardinality']
            else:
                maxcard = 1
            node = (rel.start_node['DENo'], mincard, maxcard)
            result.extend(serialise(session, path + [node]))
        result.append('!')

    return result

def createQuery(path):
    expr = []
    expr.append("(:Node {{DENo:'{value}'}})".format(value=path[0][0]))
    
    for i in range(1, len(path)):
        expr.append("<-[:CHILD_OF]-")
        expr.append("(:Node {{DENo:'{value}'}})".format(value=path[i][0]))

    # The last relation and the last node must have variables attached, as they are the ones
    # I want returned.
    expr.append("<-[r:CHILD_OF]-")
    expr.append("(n:Node)")
    expr.append(' return n,r')
    return 'MATCH ' + ''.join(expr)

userid = sys.argv[1]
password = sys.argv[2]
driver = GraphDatabase.driver("bolt://localhost:7687", auth=(userid, password))

with driver.session() as session:
    # Requirement for this: User needs to know the key of the root node,
    # used as second argument in call to serialiseGraph.
    result = serialiseGraph(session, '1')
    print('\n'.join(result))

# MATCH (:Node {name: 'ROOT', DENo: '1'})<-[:CHILD_OF {mincardinality: 1, maxcardinality: 1}]-(:Node {name: 'A', DENo: '2'})<-[:CHILD_OF {mincardinality: 1, maxcardinality: 99999}]-(:Node {name: 'B', DENo: '4'})<-[r:CHILD_OF]-(n:Node) return n,r;