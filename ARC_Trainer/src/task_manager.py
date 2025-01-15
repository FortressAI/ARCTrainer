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

    def submit_task(self, task_data):
        """
        Submits a task to the Neo4j database.

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
                return {"task_id": task_id, "status": "queued"}
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
