from neo4j import GraphDatabase
from app.config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
    def close(self):
        self.driver.close()
        
    def execute_query(self, query: str, parameters: dict = None):
        with self.driver.session() as session:
            return session.run(query, parameters)

# Singleton instance
neo4j_manager = Neo4jManager()