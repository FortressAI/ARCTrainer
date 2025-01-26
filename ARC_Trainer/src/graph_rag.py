import os
import json
from neo4j import GraphDatabase
from loguru import logger

class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized and connected to Neo4j.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def store_solution(self, task_name, solution):
        """Stores an AI-generated solution in the knowledge graph."""
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (t:Task {name: $task_name})
                    SET t.solution = $solution
                    """,
                    task_name=task_name,
                    solution=json.dumps(solution)
                )
            logger.info(f"Solution for {task_name} stored successfully.")
        except Exception as e:
            logger.error(f"Error storing solution for {task_name}: {e}")

    def detect_contradictions(self, task_name):
        """Detects contradictions between stored AI solutions in the knowledge graph."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {name: $task_name})
                    RETURN t.solution AS solution
                    """,
                    task_name=task_name
                )
                solutions = [record["solution"] for record in result]
                if len(set(solutions)) > 1:
                    logger.warning(f"Contradictions detected for task {task_name}.")
                    return {"status": "contradiction", "solutions": solutions}
                else:
                    return {"status": "consistent", "solution": solutions[0]}
        except Exception as e:
            logger.error(f"Error detecting contradictions for {task_name}: {e}")
            return {"error": "Internal server error"}

    def query_solution(self, task_name):
        """Retrieves the stored solution for a given ARC task."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {name: $task_name})
                    RETURN t.solution AS solution
                    """,
                    task_name=task_name
                )
                record = result.single()
                if record:
                    return json.loads(record["solution"])
                else:
                    return {"error": "No solution found for this task."}
        except Exception as e:
            logger.error(f"Error querying solution for {task_name}: {e}")
            return {"error": "Internal server error"}

if __name__ == "__main__":
    graph_rag = GraphRAG()
    graph_rag.close()
