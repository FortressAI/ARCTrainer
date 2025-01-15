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

    def submit_feedback(self, session_id, feedback):
        """
        Stores user feedback in the database.

        Args:
            session_id (str): Unique identifier for the user session.
            feedback (dict): Feedback data submitted by the user.

        Returns:
            bool: True if feedback was stored successfully, False otherwise.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (s:Session {id: $session_id})
                    CREATE (f:Feedback {data: $feedback})
                    MERGE (s)-[:HAS_FEEDBACK]->(f)
                    """,
                    session_id=session_id, feedback=feedback
                )
                logger.info(f"Feedback for session {session_id} stored successfully.")
                return True
        except Exception as e:
            logger.error(f"Error storing feedback for session {session_id}: {e}")
            return False

    def get_feedback(self, session_id):
        """
        Retrieves feedback for a given session ID from the database.

        Args:
            session_id (str): Unique identifier for the user session.

        Returns:
            list: Feedback data if found, empty list otherwise.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (s:Session {id: $session_id})-[:HAS_FEEDBACK]->(f:Feedback)
                    RETURN f.data AS feedback
                    """,
                    session_id=session_id
                )
                feedback_list = [record["feedback"] for record in result]

                if feedback_list:
                    logger.info(f"Retrieved feedback for session {session_id}.")
                    return feedback_list
                else:
                    logger.warning(f"No feedback found for session {session_id}.")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving feedback for session {session_id}: {e}")
            return []

if __name__ == "__main__":
    feedback_module = UserFeedback()

    session_id = "example_session_id"
    feedback = {"user": "test_user", "comment": "Great task!", "rating": 5}

    # Submit feedback
    success = feedback_module.submit_feedback(session_id, feedback)
    print("Feedback submitted:", success)

    # Retrieve feedback
    retrieved_feedback = feedback_module.get_feedback(session_id)
    print("Retrieved Feedback:", retrieved_feedback)

    feedback_module.close()
