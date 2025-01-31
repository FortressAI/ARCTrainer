# File: ARC_Trainer/src/graph_rag.py

import os
import json
from neo4j import GraphDatabase
from loguru import logger

class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="mysecurepassword"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized and connected to Neo4j.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def store_solution(self, task_name, solution):
        """Stores an AI-generated solution JSON in Neo4j."""
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
        """
        Example method: Checks if multiple different solutions are stored for the same puzzle,
        and flags a contradiction if so.
        """
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
                # If multiple distinct solutions, we consider that a contradiction
                if len(set(solutions)) > 1:
                    logger.warning(f"Contradictions detected for task {task_name}.")
                    return {"status": "contradiction", "solutions": solutions}
                else:
                    if solutions:
                        return {"status": "consistent", "solution": solutions[0]}
                    else:
                        return {"status": "consistent", "solution": None}
        except Exception as e:
            logger.error(f"Error detecting contradictions for {task_name}: {e}")
            return {"error": "Internal server error"}

    def query_solution(self, task_name):
        """Retrieves stored solution from Neo4j for a given puzzle."""
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
                if record and record["solution"]:
                    return json.loads(record["solution"])
                else:
                    return {"error": "No solution found for this task."}
        except Exception as e:
            logger.error(f"Error querying solution for {task_name}: {e}")
            return {"error": "Internal server error"}

    # -------------------------------
    # NEW DEBATE-RELATED METHODS
    # -------------------------------

    def store_debate_message(self, task_name, message, timestamp):
        """
        Stores a single line of 'debate log' under a given puzzle (Task) in the KG.
        Each message is a node :DebateLog with a 'text' property and 'timestamp'.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (t:Task {name: $task_name})
                    MERGE (d:DebateLog {timestamp: $timestamp})
                    SET d.text = $message
                    MERGE (t)-[:HAS_DEBATE]->(d)
                    """,
                    task_name=task_name,
                    timestamp=timestamp,
                    message=message
                )
            logger.info(f"Debate message stored for {task_name}: {message}")
        except Exception as e:
            logger.error(f"Error storing debate message: {e}")

    def fetch_debate_history(self, task_name=None):
        """
        Retrieves all debate log messages from the KG, optionally filtered by puzzle name.
        Returns a list of dicts like [{text: "...", timestamp: 12345678}, ...].
        """
        logs = []
        try:
            with self.driver.session() as session:
                if task_name:
                    result = session.run(
                        """
                        MATCH (t:Task {name: $task_name})-[:HAS_DEBATE]->(d:DebateLog)
                        RETURN d.text AS text, d.timestamp AS timestamp
                        ORDER BY d.timestamp
                        """,
                        task_name=task_name
                    )
                else:
                    result = session.run(
                        """
                        MATCH (d:DebateLog)
                        RETURN d.text AS text, d.timestamp AS timestamp
                        ORDER BY d.timestamp
                        """
                    )
                for record in result:
                    logs.append({
                        "text": record["text"],
                        "timestamp": record["timestamp"]
                    })
        except Exception as e:
            logger.error(f"Error fetching debate history: {e}")
        return logs

if __name__ == "__main__":
    # Example usage
    logger.info("Testing GraphRAG as main...")
    rag = GraphRAG()
    # Maybe do some quick tests, e.g. rag.store_solution("myTask", [{"grid": 1}])
    rag.close()
