from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from loguru import logger
import uuid

app = Flask(__name__)

class TaskManager:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Task Manager with Neo4j.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("TaskManager initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def validate_task_with_knowledge_graph(self, task_id):
        """
        Validates a task by checking the AI knowledge graph for contradictions.

        Args:
            task_id (str): Unique identifier for the task.

        Returns:
            bool: True if the task is valid, False otherwise.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:USES_RULE]->(r:Rule)
                    OPTIONAL MATCH (c:Contradiction)-[:CONFLICTS_WITH]->(r)
                    RETURN COUNT(c) AS contradictions
                    """,
                    task_id=task_id
                )

                record = result.single()
                if record and record["contradictions"] > 0:
                    logger.warning(f"Task {task_id} conflicts with existing AI knowledge.")
                    return False

                logger.info(f"Task {task_id} passed knowledge graph validation.")
                return True
        except Exception as e:
            logger.error(f"Error validating task {task_id} with knowledge graph: {e}")
            return False

    def track_task_decision_path(self, task_id, decision):
        """
        Logs the AI's decision-making path for a task in the knowledge graph.

        Args:
            task_id (str): Unique identifier for the task.
            decision (dict): The AI's decision reasoning data.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    MERGE (d:Decision {id: $task_id, decision_data: $decision})
                    MERGE (t)-[:RESULTED_IN]->(d)
                    """,
                    task_id=task_id,
                    decision=decision
                )
                logger.info(f"Stored decision path for task {task_id}.")
        except Exception as e:
            logger.error(f"Error tracking decision path for task {task_id}: {e}")

    def submit_task(self, task_data):
        """
        Submits a task to the Neo4j database, ensuring it meets AI safety requirements.

        Args:
            task_data (dict): Data for the task to be processed.

        Returns:
            dict: Task ID and status.
        """
        try:
            task_id = str(uuid.uuid4())
            with self.driver.session() as session:
                session.run(
                    """
                    CREATE (t:Task {id: $task_id, status: 'queued', data: $task_data})
                    """,
                    task_id=task_id, task_data=task_data
                )
                logger.info(f"Task {task_id} submitted successfully.")

                # Validate the task using the AI knowledge graph
                if not self.validate_task_with_knowledge_graph(task_id):
                    session.run(
                        """
                        MATCH (t:Task {id: $task_id})
                        SET t.status = 'failed'
                        """,
                        task_id=task_id
                    )
                    logger.warning(f"Task {task_id} rejected due to conflicts in AI knowledge graph.")
                    return {"task_id": task_id, "status": "failed", "reason": "Knowledge graph conflict"}

                # Mark as ready for execution
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    SET t.status = 'ready'
                    """,
                    task_id=task_id
                )
                logger.info(f"Task {task_id} passed all safety checks and is ready for execution.")
                return {"task_id": task_id, "status": "ready"}
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            return {"error": "Failed to submit task"}

    def get_task_status(self, task_id):
        """
        Retrieves the status and metadata of a task from Neo4j.

        Args:
            task_id (str): ID of the task.

        Returns:
            dict: Task status and metadata if found.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    RETURN t.status AS status, t.data AS data
                    """,
                    task_id=task_id
                )
                record = result.single()
                if record:
                    logger.info(f"Task {task_id} status retrieved successfully.")
                    return {"status": record["status"], "data": record["data"]}
                else:
                    logger.warning(f"Task {task_id} not found.")
                    return {"error": "Task not found"}
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            return {"error": "Internal server error"}

@app.route("/tasks", methods=["POST"])
def submit_task():
    """
    API endpoint to submit a task.
    """
    try:
        task_data = request.json

        if not task_data:
            return jsonify({"error": "Task data is required"}), 400

        manager = TaskManager()
        response = manager.submit_task(task_data)
        manager.close()
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in submit_task endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/tasks/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """
    API endpoint to get the status of a task.
    """
    try:
        manager = TaskManager()
        response = manager.get_task_status(task_id)
        manager.close()
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in get_task_status endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Task Manager API")
    app.run(host="0.0.0.0", port=5002)
