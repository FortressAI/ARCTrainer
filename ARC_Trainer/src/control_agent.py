from neo4j import GraphDatabase
from loguru import logger
from pyswip import Prolog
from graph_rag import GraphRAG
from user_feedback import UserFeedback

class ControlAgent:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", config_file="config.json"):
        """
        Initializes the Control Agent with Neo4j, Prolog, and auxiliary components.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            config_file (str): Path to the configuration file.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.prolog = Prolog()
        self.graph_rag = GraphRAG(uri, user, password)
        self.user_feedback = UserFeedback(uri, user, password)
        self.config_file = config_file
        self._load_config()
        self._load_prolog_rules()
        logger.info("ControlAgent initialized.")

    def close(self):
        """Closes all connections to the Neo4j database."""
        self.driver.close()
        self.graph_rag.close()
        self.user_feedback.close()

    def _load_config(self):
        """Loads the configuration file."""
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = {}

    def _load_prolog_rules(self):
        """Loads Prolog rules from the configuration."""
        try:
            prolog_files = self.config.get("prolog_rules", [])
            for file in prolog_files:
                self.prolog.consult(file)
                logger.info(f"Prolog rules loaded from {file}.")
        except Exception as e:
            logger.error(f"Error loading Prolog rules: {e}")

    def process_task(self, task_id):
        """
        Processes a task using the graph manager and updates the task status.

        Args:
            task_id (str): Task ID to process.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    RETURN t.data AS data
                    """,
                    task_id=task_id
                )

                record = result.single()
                if not record:
                    logger.warning(f"Task {task_id} not found.")
                    return

                task_data = record["data"]
                logger.info(f"Processing task {task_id} with data: {task_data}.")

                # Add your task-specific processing logic here

                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    SET t.status = 'completed'
                    """,
                    task_id=task_id
                )
                logger.info(f"Task {task_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")

    def handle_feedback(self, session_id, feedback):
        """
        Handles user feedback and updates system metrics.

        Args:
            session_id (str): Session ID for feedback.
            feedback (dict): Feedback data.
        """
        try:
            success = self.user_feedback.submit_feedback(session_id, feedback)
            if success:
                logger.info(f"Feedback for session {session_id} handled successfully.")
            else:
                logger.warning(f"Failed to handle feedback for session {session_id}.")
        except Exception as e:
            logger.error(f"Error handling feedback for session {session_id}: {e}")

if __name__ == "__main__":
    agent = ControlAgent()

    # Example usage
    task_id = "example_task_id"
    session_id = "example_session_id"
    feedback = {"user": "test_user", "comment": "Great task!", "rating": 5}

    agent.process_task(task_id)
    agent.handle_feedback(session_id, feedback)

    agent.close()
