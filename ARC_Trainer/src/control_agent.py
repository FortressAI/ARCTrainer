from neo4j import GraphDatabase
from loguru import logger
from pyswip import Prolog
from src.graph_rag import GraphRAG
from src.user_feedback import UserFeedback
from src.llm_fine_tuner import LLMFineTuner

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
        self.llm_fine_tuner = LLMFineTuner(uri, user, password)
        self.config_file = config_file
        self._load_config()
        self._load_prolog_rules()
        logger.info("ControlAgent initialized.")

    def close(self):
        """Closes all connections to the Neo4j database."""
        self.driver.close()
        self.graph_rag.close()
        self.user_feedback.close()
        self.llm_fine_tuner.close()

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

    def monitor_ai_decisions(self, task_id):
        """
        Monitors AI decisions and flags reasoning errors for correction.

        Args:
            task_id (str): Task ID to monitor.

        Returns:
            dict: AI decision audit report.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:USES_RULE]->(r:Rule)
                    RETURN t.data AS task_data, r.id AS rule_id, r.causal_validation AS validation
                    """,
                    task_id=task_id
                )

                audit_results = []
                for record in result:
                    validation_status = record["validation"]
                    if not validation_status:
                        audit_results.append({
                            "task_id": task_id,
                            "rule_id": record["rule_id"],
                            "error": "Causal validation failed"
                        })
                        self.correct_ai_reasoning(task_id, record["rule_id"])

                if audit_results:
                    logger.warning(f"AI decision audit flagged issues: {audit_results}")
                else:
                    logger.info(f"AI decision audit passed for task {task_id}.")

                return {"task_id": task_id, "audit_results": audit_results}
        except Exception as e:
            logger.error(f"Error monitoring AI decisions for task {task_id}: {e}")
            return {"error": "Failed to audit AI decisions"}

    def correct_ai_reasoning(self, task_id, rule_id):
        """
        Corrects AI reasoning errors by modifying faulty rules.

        Args:
            task_id (str): Task ID associated with the faulty reasoning.
            rule_id (str): Rule ID that failed validation.
        """
        try:
            with self.driver.session() as session:
                feedback = self.user_feedback.get_feedback(task_id)

                if not feedback:
                    logger.info(f"No feedback available to correct AI reasoning for task {task_id}.")
                    return

                for entry in feedback:
                    correction = entry.get("correction")
                    if correction:
                        session.run(
                            """
                            MATCH (r:Rule {id: $rule_id})
                            SET r.definition = $correction, r.causal_validation = true
                            """,
                            rule_id=rule_id,
                            correction=correction
                        )
                        logger.info(f"AI reasoning corrected for rule {rule_id} using user feedback.")

        except Exception as e:
            logger.error(f"Error correcting AI reasoning for rule {rule_id}: {e}")

    def enforce_socratic_questioning(self, task_id):
        """
        Enforces Socratic questioning to ensure AI justifies its decisions logically.

        Args:
            task_id (str): Task ID to enforce questioning.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:USES_RULE]->(r:Rule)
                    RETURN r.id AS rule_id, r.definition AS rule_definition
                    """,
                    task_id=task_id
                )

                for record in result:
                    rule_id = record["rule_id"]
                    rule_definition = record["rule_definition"]

                    socratic_prompt = f"Why is the following rule valid? '{rule_definition}' Explain its causal logic."
                    response = self.llm_fine_tuner.query_llm(socratic_prompt)

                    if not response or "error" in response:
                        session.run(
                            """
                            MATCH (r:Rule {id: $rule_id})
                            SET r.socratic_validated = false
                            """,
                            rule_id=rule_id
                        )
                        logger.warning(f"Rule {rule_id} failed Socratic questioning validation.")
                    else:
                        session.run(
                            """
                            MATCH (r:Rule {id: $rule_id})
                            SET r.socratic_validated = true
                            """,
                            rule_id=rule_id
                        )
                        logger.info(f"Rule {rule_id} passed Socratic questioning validation.")

        except Exception as e:
            logger.error(f"Error enforcing Socratic questioning for task {task_id}: {e}")

    def audit_ai_trust(self):
        """
        Audits the overall AI trust score and flags inconsistencies.

        Returns:
            dict: Trust audit results.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task)
                    RETURN t.id AS task_id, t.ai_trust_score AS trust_score
                    """
                )

                audit_results = []
                for record in result:
                    if record["trust_score"] < 0.7:
                        audit_results.append({
                            "task_id": record["task_id"],
                            "trust_score": record["trust_score"],
                            "error": "Low AI trust score"
                        })

                if audit_results:
                    logger.warning(f"AI trust audit flagged issues: {audit_results}")
                else:
                    logger.info("AI trust audit passed.")

                return {"audit_results": audit_results}
        except Exception as e:
            logger.error(f"Error auditing AI trust scores: {e}")
            return {"error": "Failed to audit AI trust scores"}

if __name__ == "__main__":
    agent = ControlAgent()

    # Example: Monitor AI decision-making
    audit_results = agent.monitor_ai_decisions("example_task_id")
    print("AI Decision Audit Results:", audit_results)

    # Example: Enforce Socratic questioning
    agent.enforce_socratic_questioning("example_task_id")

    # Example: Audit AI trust scores
    trust_results = agent.audit_ai_trust()
    print("AI Trust Audit Results:", trust_results)

    agent.close()
