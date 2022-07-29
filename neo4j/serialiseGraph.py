import sys
from neo4j import GraphDatabase

# Serialise a Neo4j tree graph.
# This uses relationships, as that is where the cardinality is stored.
#-----------------------------------------------------------------------

def serialiseGraph(session, rootdeno):
    result = []
    serialise(session, rootdeno, result)
    return result

def serialise(session, deno, result, path=[]):
    print('Node:', deno, 'Path:', path)
    query = createQuery(deno)
    g = session.read_transaction( lambda tx: tx.run(query,).graph())
    result.append(deno)

    if len(g.relationships) == 0:
        result.append('!')
        return result
    else:
        for rel in g.relationships:
            #if rel['maxcardinality'] != 1:
            #    result.append(rel.start_node['DENo'] + '/' + str(rel['maxcardinality']))
            #else:
            #    result.append(rel.start_node['DENo'])
            serialise(session, rel.start_node['DENo'], result, path + [rel.start_node['name']])
        result.append('!')

def createQuery(deno):
    # TODO: serialisering skal tage højde for forældre i alle led bagud/opad, ikke kun den umiddelbare forælder.
    # Ellers går det galt, når den samme node indgår i forskellige sammenhænge.
    # Dvs. query skal opbygges i takt med at man bevæger sig rundt i grafen, så den fanger alle led i 
    # den aktuelle sti (som i createGraf.py).
    return "MATCH (n:Node)-[r:CHILD_OF]->(:Node {DENo:'" + deno + "'}) return n,r;"

userid = sys.argv[1]
password = sys.argv[2]
driver = GraphDatabase.driver("bolt://localhost:7687", auth=(userid, password))

with driver.session() as session:
    result = serialiseGraph(session, '1')
    print('\n'.join(result))
