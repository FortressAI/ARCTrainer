from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from loguru import logger
from src.llm_client import LLMClient
from src.learning_agent import LearningAgent

app = Flask(__name__)

class UserFeedbackManager:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the User Feedback Manager.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.llm_client = LLMClient()
        self.learning_agent = LearningAgent()

        logger.info("UserFeedbackManager initialized with multi-domain ontology support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def store_feedback(self, rule_id, feedback_text, user_id, domain):
        """
        Stores user feedback for a specific ontology rule.

        Args:
            rule_id (str): Unique identifier of the ontology rule.
            feedback_text (str): User feedback.
            user_id (str): Unique identifier of the user providing feedback.
            domain (str): Ontology category (e.g., legal, healthcare, AI ethics, finance).

        Returns:
            dict: Feedback storage confirmation.
        """
        try:
            feedback_id = f"feedback_{hash(feedback_text) % 100000}"

            with self.driver.session() as session:
                session.run(
                    """
                    CREATE (f:Feedback {id: $feedback_id, rule_id: $rule_id, feedback_text: $feedback_text,
                    user_id: $user_id, domain: $domain, status: 'pending'})
                    """,
                    feedback_id=feedback_id, rule_id=rule_id, feedback_text=feedback_text,
                    user_id=user_id, domain=domain
                )

            logger.info(f"Feedback stored for rule {rule_id} in domain '{domain}'.")
            return {"feedback_id": feedback_id, "status": "stored"}

        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
            return {"error": "Failed to store feedback"}

    def refine_rule_based_on_feedback(self, rule_id, domain):
        """
        Refines an ontology rule based on user feedback.

        Args:
            rule_id (str): Unique identifier of the ontology rule.
            domain (str): Ontology category.

        Returns:
            dict: Updated rule details.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (f:Feedback)-[:RELATES_TO]->(r:OntologyRule {id: $rule_id})
                    WHERE r.domain = $domain AND f.status = 'pending'
                    RETURN f.feedback_text AS feedback_text
                    """,
                    rule_id=rule_id, domain=domain
                )

                feedback_list = [record["feedback_text"] for record in result]

                if not feedback_list:
                    return {"error": "No pending feedback for this rule"}

                feedback_combined = " ".join(feedback_list)

                # AI-powered refinement based on feedback
                refined_cnl = self.llm_client.query_llm(f"Improve this ontology rule based on user feedback: {feedback_combined}")
                refined_prolog = self.llm_client.query_llm(f"Convert this refined rule into Prolog: {refined_cnl['response']}")

                # Update rule in Neo4j
                session.run(
                    """
                    MATCH (r:OntologyRule {id: $rule_id})
                    SET r.cnl_rule = $refined_cnl, r.prolog_rule = $refined_prolog
                    """,
                    rule_id=rule_id, refined_cnl=refined_cnl["response"], refined_prolog=refined_prolog["response"]
                )

                # Mark feedback as processed
                session.run(
                    """
                    MATCH (f:Feedback)-[:RELATES_TO]->(r:OntologyRule {id: $rule_id})
                    SET f.status = 'processed'
                    """,
                    rule_id=rule_id
                )

                logger.info(f"Ontology rule {rule_id} refined using user feedback in domain '{domain}'.")
                return {
                    "rule_id": rule_id,
                    "updated_cnl_rule": refined_cnl["response"],
                    "updated_prolog_rule": refined_prolog["response"]
                }

        except Exception as e:
            logger.error(f"Error refining rule {rule_id}: {e}")
            return {"error": "Ontology refinement failed"}

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    API endpoint to submit feedback for an ontology rule.
    """
    try:
        data = request.json
        rule_id = data.get("rule_id")
        feedback_text = data.get("feedback_text")
        user_id = data.get("user_id")
        domain = data.get("domain")

        if not rule_id or not feedback_text or not user_id or not domain:
            return jsonify({"error": "Missing required parameters"}), 400

        manager = UserFeedbackManager()
        response = manager.store_feedback(rule_id, feedback_text, user_id, domain)
        manager.close()
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in submit_feedback endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/refine_rule", methods=["POST"])
def refine_rule():
    """
    API endpoint to refine an ontology rule based on user feedback.
    """
    try:
        data = request.json
        rule_id = data.get("rule_id")
        domain = data.get("domain")

        if not rule_id or not domain:
            return jsonify({"error": "Missing required parameters"}), 400

        manager = UserFeedbackManager()
        response = manager.refine_rule_based_on_feedback(rule_id, domain)
        manager.close()
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in refine_rule endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting User Feedback Manager API")
    app.run(host="0.0.0.0", port=5003)
