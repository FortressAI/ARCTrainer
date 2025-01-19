from neo4j import GraphDatabase
from loguru import logger

class UserFeedback:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the User Feedback module with Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("UserFeedback initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def submit_feedback(self, session_id, task_id, feedback, rating, correction=None):
        """
        Stores user feedback in the database.

        Args:
            session_id (str): Unique identifier for the user session.
            task_id (str): ID of the task being reviewed.
            feedback (str): User's qualitative feedback.
            rating (int): Rating given by the user (1-5 scale).
            correction (str, optional): A user-provided correction to improve AI reasoning.

        Returns:
            bool: True if feedback was stored successfully, False otherwise.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    MERGE (s:Session {id: $session_id})
                    CREATE (f:Feedback {feedback: $feedback, rating: $rating, correction: $correction})
                    MERGE (s)-[:HAS_FEEDBACK]->(f)
                    MERGE (t)-[:RECEIVED_FEEDBACK]->(f)
                    """,
                    session_id=session_id,
                    task_id=task_id,
                    feedback=feedback,
                    rating=rating,
                    correction=correction
                )
                logger.info(f"Feedback stored for session {session_id} on task {task_id}.")
                return True
        except Exception as e:
            logger.error(f"Error storing feedback for session {session_id} on task {task_id}: {e}")
            return False

    def get_feedback(self, task_id):
        """
        Retrieves all feedback for a given AI-generated task.

        Args:
            task_id (str): Unique identifier for the task.

        Returns:
            list: Feedback data if found, empty list otherwise.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:RECEIVED_FEEDBACK]->(f:Feedback)
                    RETURN f.feedback AS feedback, f.rating AS rating, f.correction AS correction
                    """,
                    task_id=task_id
                )

                feedback_list = [
                    {
                        "feedback": record["feedback"],
                        "rating": record["rating"],
                        "correction": record["correction"]
                    }
                    for record in result
                ]

                if feedback_list:
                    logger.info(f"Retrieved feedback for task {task_id}.")
                    return feedback_list
                else:
                    logger.warning(f"No feedback found for task {task_id}.")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving feedback for task {task_id}: {e}")
            return []

    def update_ai_trust_score(self, task_id):
        """
        Updates AI trust score based on user feedback.

        Args:
            task_id (str): Unique identifier for the AI task.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:RECEIVED_FEEDBACK]->(f:Feedback)
                    RETURN avg(f.rating) AS average_rating
                    """,
                    task_id=task_id
                )

                record = result.single()
                if record and record["average_rating"] is not None:
                    trust_score = record["average_rating"] / 5.0  # Normalize to a 0-1 scale
                    session.run(
                        """
                        MATCH (t:Task {id: $task_id})
                        SET t.ai_trust_score = $trust_score
                        """,
                        task_id=task_id,
                        trust_score=trust_score
                    )
                    logger.info(f"Updated AI trust score for task {task_id} to {trust_score}.")
        except Exception as e:
            logger.error(f"Error updating AI trust score for task {task_id}: {e}")

    def apply_corrections_to_rules(self, task_id):
        """
        If users provide corrections, this method updates AI-generated rules accordingly.

        Args:
            task_id (str): Unique identifier for the task.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:RECEIVED_FEEDBACK]->(f:Feedback)
                    WHERE f.correction IS NOT NULL
                    RETURN f.correction AS correction
                    """,
                    task_id=task_id
                )

                corrections = [record["correction"] for record in result if record["correction"]]

                if corrections:
                    for correction in corrections:
                        session.run(
                            """
                            MATCH (r:Rule)
                            WHERE r.definition CONTAINS $correction
                            SET r.causal_validation = true
                            """,
                            correction=correction
                        )
                        logger.info(f"Applied user correction to rule: {correction}")

                    logger.info(f"Updated AI rules based on user feedback for task {task_id}.")
        except Exception as e:
            logger.error(f"Error applying corrections for task {task_id}: {e}")

if __name__ == "__main__":
    feedback_module = UserFeedback()

    # Example: Submit feedback
    success = feedback_module.submit_feedback(
        session_id="session_123",
        task_id="task_456",
        feedback="The AI explanation was unclear.",
        rating=3,
        correction="AI should explain why causation applies, not just correlation."
    )
    print("Feedback submitted:", success)

    # Example: Retrieve feedback
    retrieved_feedback = feedback_module.get_feedback("task_456")
    print("Retrieved Feedback:", retrieved_feedback)

    # Example: Update AI trust score
    feedback_module.update_ai_trust_score("task_456")

    # Example: Apply corrections to rules
    feedback_module.apply_corrections_to_rules("task_456")

    feedback_module.close()
