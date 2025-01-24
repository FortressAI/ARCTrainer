from neo4j import GraphDatabase
from loguru import logger

class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized.")

    def close(self):
        self.driver.close()

    def store_reasoning_challenge(self, image_caption, reasoning_prompt):
        """Stores AI-generated reasoning challenges in Neo4j Knowledge Graph."""
        with self.driver.session() as session:
            session.run(
                """
                CREATE (c:ReasoningChallenge {caption: $image_caption, prompt: $reasoning_prompt})
                """, 
                image_caption=image_caption, 
                reasoning_prompt=reasoning_prompt
            )
            logger.info("Stored reasoning challenge in Knowledge Graph.")

if __name__ == "__main__":
    graph_rag = GraphRAG()
    graph_rag.store_reasoning_challenge("A cat sitting on a chair", "What reasoning patterns can be derived?")
