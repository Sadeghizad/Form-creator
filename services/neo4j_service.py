from neo4j import GraphDatabase

class Neo4jService:
    def __init__(self, uri, username, password):
        self._driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self._driver.close()

    def execute_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

# Initialize Neo4jService instance
neo4j_service = Neo4jService(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="Y0u4r34mazin6"
)
def save_user_report(user_id, form_id, report_data):
    query = """
    MERGE (u:User {id: $user_id})
    MERGE (f:Form {id: $form_id})
    MERGE (u)-[:ANSWERED]->(r:Report {generated_at: datetime(), data: $report_data})
    MERGE (r)-[:FOR_FORM]->(f)
    RETURN r
    """
    parameters = {
        "user_id": user_id,
        "form_id": form_id,
        "report_data": report_data
    }
    return neo4j_service.execute_query(query, parameters)
