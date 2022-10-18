import graphlib
from select import select
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import logging
import sys


db_uri = 'bolt://localhost:7687'
auth_name = 'neo4j'
auth_password = 'password'

testData = {
    'identity': 1,
    'labels': ['testLabel1'],
    'properties': {
        'name': 'CityTest'
    }
}

testData2 = {
    'name': 'CityTestBrno'
}




class Neo4jDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    # Don't forget to close the driver connection when you are finished with it
    def close(self):
        self.driver.close()

    @staticmethod
    def enable_log(level, output_stream):
        handler = logging.StreamHandler(output_stream)
        handler.setLevel(level)
        logging.getLogger("neo4j").addHandler(handler)
        logging.getLogger("neo4j").setLevel(level)


    def create_rel(self,  query, name1, name2, relation ):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_rel, query, name1, name2, relation)
            """ for row in result:
                print("Created relation between: {p1}, {p2} from {relation}"
                      .format(
                          p1=row['p1'],
                          p2=row['p2'],
                          relation=row["relation"])) """

    @staticmethod
    def _create_and_return_rel(tx, query, name1, name2, relation ):
        try:
            tx.run(query, name1=name1, name2=name2, relation=relation)
        
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    
    def deleteAll(self):
        query = (
            "MATCH (n) "
            "OPTIONAL MATCH (n)-[r]-() "
            "DELETE n, r "
            "RETURN count(n) as deletedNodesCount"
        )
        with self.driver.session() as session:
            result = session.run(query)
            print(result)
            for row in result:
                print(f"Found row: {row}")
        
        return



if __name__ == "__main__":
    bolt_url = db_uri
    user = auth_name
    password = auth_password
    Neo4jDB.enable_log(logging.INFO, sys.stdout)
    app = Neo4jDB(bolt_url, user, password)



    queryA = (
            "MERGE (a:File { name: $name1 }) "
            "MERGE (b:File { name: $name2 }) "
            "MERGE (a)-[pr:PRECEEDS { from: $relation }]->(b) "
            "RETURN a, b, pr"
            )

    app.create_rel(queryA, 'MayFile', 'JuneFile', 'PRECEEDS')
    app.close()



    queryB = (
            "MERGE (a:File { name: $name1 }) "
            "MERGE (b:Path { name: $name2 }) "
            "MERGE (a)-[d:DEFINES { from: $relation }]->(b) "
            "RETURN a, b, d"
            )

    queryC = (
            "MERGE (a:Path { name: $name1 }) "
            "MERGE (b:Path { name: $name2 }) "
            "MERGE (a)-[c:CANCELS { from: $relation }]->(b) "
            "RETURN a, b, c"
            )

    queryD = (
            "MERGE (a:Path { name: $name1 }) "
            "MERGE (b:Path { name: $name2 }) "
            "MERGE (a)-[r:RELATED { from: $relation }]->(b) "
            "RETURN a, b, r"
            )

    queryE = (
            "MERGE (a:Path { name: $name1 }) "
            "MERGE (b:Train { name: $name2 }) "
            "MERGE (a)-[sb:SERVED_BY { from: $relation }]->(b) "
            "RETURN a, b, sb"
            )

    queryF = (
            "MERGE (a:Path { name: $name1 }) "
            "MERGE (b:Day { name: $name2 }) "
            "MERGE (a)-[gi:GOES_IN { from: $relation }]->(b) "
            "RETURN a, b, gi"
            )

    queryG = (
            "MERGE (a:Path { name: $name1 }) "
            "MERGE (b:Station { name: $name2 }) "
            "MERGE (a)-[in:IS_IN { from: $relation }]->(b) "
            "RETURN a, b, cin"
            )