import logging
import sys

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class Neo4JWriter:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    @staticmethod
    def enable_log():
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        logging.getLogger("neo4j").addHandler(handler)
        logging.getLogger("neo4j").setLevel(logging.INFO)

    def createStatement(self, command):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(self._createStatement, command)
    
    def create_dataelement(self, node):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_dataelement, node['name'], node['DENo'])

    def create_childrelation(self, childnode, parentdeno, cardinality):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_childrelation, childnode['name'], childnode['DENo'], parentdeno, cardinality)

    # Example method from Neo4j.
    def create_friendship(self, person1_name, person2_name, knows_from):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_friendship, person1_name, person2_name, knows_from)
            for row in result:
                print("Created friendship between: {p1}, {p2} from {knows_from}"
                      .format(
                          p1=row['p1'],
                          p2=row['p2'],
                          knows_from=row["knows_from"]))

    @staticmethod
    def _createStatement(tx, command):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        result = tx.run(command)
        
    def _create_dataelement(tx, name, deno):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (:Node { name: $name, DENo: $deno }) "
        )
        result = tx.run(query, name=name, deno=deno)

    @staticmethod
    def _create_childrelation(tx, childname, childdeno, parentdeno, cardinality):
        query = (
            "MATCH (n:Node {DENo: $parentdeno}) "
            "CREATE (:Node { name: $childname, DENo: $childdeno })-[:CHILD_OF {cardinality: $cardinality}]->(n)"
        )
        result = tx.run(query, childname=childname, childdeno=childdeno, parentdeno=parentdeno, cardinality=cardinality)

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name, knows_from):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[k:KNOWS { from: $knows_from }]->(p2) "
            "RETURN p1, p2, k"
        )
        result = tx.run(query, person1_name=person1_name,
                        person2_name=person2_name, knows_from=knows_from)
        try:
            return [{
                        "p1": row["p1"]["name"],
                        "p2": row["p2"]["name"],
                        "knows_from": row["k"]["from"]
                    }
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]


if __name__ == "__main__":
    bolt_url = 'bolt://localhost:7687'
    user = sys.argv[1]
    password = sys.argv[2]
    Graphwriter.enable_log(logging.INFO, sys.stdout)
    app = Graphwriter(bolt_url, user, password)
    node = { 'name': 'Declaration', 'DENo': '01'}
    app.create_dataelement(node)
    childnode = { 'name': 'Declaration type', 'DENo': '11 01 000 000'}
    app.create_childrelation(childnode, node['DENo'], 1)
    app.close()