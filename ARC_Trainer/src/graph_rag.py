from neo4j import GraphDatabase
from loguru import logger

class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Neo4j-backed Knowledge Graph.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def update_knowledge(self, task_id, task_data, result):
        """
        Updates the knowledge graph with task data and result.

        Args:
            task_id (str): Task ID.
            task_data (dict): Data related to the task.
            result (dict): Result of the task processing.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (t:Task {id: $task_id})
                    SET t.data = $task_data, t.result = $result
                    """,
                    task_id=task_id, task_data=task_data, result=result
                )
                logger.info(f"Knowledge updated for task {task_id}.")
        except Exception as e:
            logger.error(f"Error updating knowledge for task {task_id}: {e}")

    def store_counterexample(self, task_id, grid, transformed_grid):
        """
        Stores a counterexample in the knowledge graph.

        Args:
            task_id (str): Task ID associated with the counterexample.
            grid (list): Original grid data.
            transformed_grid (list): Incorrectly transformed grid.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    MERGE (ce:Counterexample {grid: $grid, transformed_grid: $transformed_grid})
                    MERGE (t)-[:HAS_COUNTEREXAMPLE]->(ce)
                    """,
                    task_id=task_id, grid=grid, transformed_grid=transformed_grid
                )
                logger.info(f"Counterexample stored for task {task_id}.")
        except Exception as e:
            logger.error(f"Error storing counterexample for task {task_id}: {e}")

    def query_knowledge(self, task_id):
        """
        Queries the knowledge graph for a specific task.

        Args:
            task_id (str): Task ID to query in the knowledge graph.

        Returns:
            dict: Data associated with the task.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    RETURN t.data AS data, t.result AS result
                    """,
                    task_id=task_id
                )
                record = result.single()
                if record:
                    logger.info(f"Data retrieved for task {task_id}.")
                    return {"data": record["data"], "result": record["result"]}
                else:
                    logger.warning(f"No data found for task {task_id}.")
                    return {}
        except Exception as e:
            logger.error(f"Error querying knowledge for task {task_id}: {e}")
            return {}

if __name__ == "__main__":
    graph = GraphRAG()

    task_id = "example_task_1"
    task_data = {"grid": [[0, 1], [1, 0]]}
    result = {"transformed_grid": [[1, 0], [0, 1]]}

    # Update knowledge graph
    graph.update_knowledge(task_id, task_data, result)

    # Store a counterexample
    counterexample_grid = [[0, 1], [1, 0]]
    counterexample_result = [[1, 1], [0, 0]]
    graph.store_counterexample(task_id, counterexample_grid, counterexample_result)

    # Query the knowledge graph
    retrieved_data = graph.query_knowledge(task_id)
    print("Retrieved Data:", retrieved_data)

    graph.close()
