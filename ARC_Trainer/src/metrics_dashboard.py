from neo4j import GraphDatabase
from loguru import logger

class MetricsDashboard:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Metrics Dashboard with Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("MetricsDashboard initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def log_causal_validation(self, rule_id, success):
        """
        Logs whether a Prolog rule passed causal validation.

        Args:
            rule_id (str): Unique identifier for the rule.
            success (bool): True if the rule passed causal validation, False otherwise.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (r:Rule {id: $rule_id})
                    SET r.causal_validation = $success
                    """,
                    rule_id=rule_id,
                    success=success
                )
                logger.info(f"Causal validation logged for rule {rule_id}: {'Passed' if success else 'Failed'}.")
        except Exception as e:
            logger.error(f"Error logging causal validation for rule {rule_id}: {e}")

    def log_ai_trust_verification(self, query, consistency_score):
        """
        Logs AI-to-AI trust verification scores.

        Args:
            query (str): The query tested across multiple AI models.
            consistency_score (float): A score between 0 and 1 indicating agreement among AI models.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (t:TrustCheck {query: $query})
                    SET t.consistency_score = $consistency_score
                    """,
                    query=query,
                    consistency_score=consistency_score
                )
                logger.info(f"Logged AI trust verification for '{query}' with score: {consistency_score}.")
        except Exception as e:
            logger.error(f"Error logging AI trust verification for '{query}': {e}")

    def log_counterfactual_failures(self, rule_id, failure_count):
        """
        Logs how often a rule fails counterfactual testing.

        Args:
            rule_id (str): Unique identifier for the rule.
            failure_count (int): Number of failed counterfactual tests.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (r:Rule {id: $rule_id})
                    SET r.counterfactual_failures = coalesce(r.counterfactual_failures, 0) + $failure_count
                    """,
                    rule_id=rule_id,
                    failure_count=failure_count
                )
                logger.info(f"Logged {failure_count} counterfactual failures for rule {rule_id}.")
        except Exception as e:
            logger.error(f"Error logging counterfactual failures for rule {rule_id}: {e}")

    def get_causal_validation_metrics(self):
        """
        Retrieves all causal validation metrics.

        Returns:
            dict: Causal validation results for all logged rules.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:Rule)
                    RETURN r.id AS rule_id, r.causal_validation AS validation
                    """
                )

                metrics = {record["rule_id"]: record["validation"] for record in result}
                logger.info(f"Fetched causal validation metrics: {metrics}")
                return metrics
        except Exception as e:
            logger.error(f"Error fetching causal validation metrics: {e}")
            return {}

    def get_ai_trust_metrics(self):
        """
        Retrieves all AI trust verification metrics.

        Returns:
            dict: AI-to-AI trust verification scores.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:TrustCheck)
                    RETURN t.query AS query, t.consistency_score AS score
                    """
                )

                metrics = {record["query"]: record["score"] for record in result}
                logger.info(f"Fetched AI trust verification metrics: {metrics}")
                return metrics
        except Exception as e:
            logger.error(f"Error fetching AI trust verification metrics: {e}")
            return {}

    def get_counterfactual_failure_metrics(self):
        """
        Retrieves all counterfactual failure logs.

        Returns:
            dict: Counterfactual failure counts for rules.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:Rule)
                    RETURN r.id AS rule_id, r.counterfactual_failures AS failures
                    """
                )

                metrics = {record["rule_id"]: record["failures"] for record in result if record["failures"] is not None}
                logger.info(f"Fetched counterfactual failure metrics: {metrics}")
                return metrics
        except Exception as e:
            logger.error(f"Error fetching counterfactual failure metrics: {e}")
            return {}

    def generate_dashboard_report(self):
        """
        Generates a comprehensive report of all key AI metrics.

        Returns:
            dict: Summary of AI validation, trust, and counterfactual testing.
        """
        try:
            report = {
                "causal_validation": self.get_causal_validation_metrics(),
                "ai_trust_verification": self.get_ai_trust_metrics(),
                "counterfactual_failures": self.get_counterfactual_failure_metrics()
            }
            logger.info(f"Generated dashboard report: {report}")
            return report
        except Exception as e:
            logger.error(f"Error generating dashboard report: {e}")
            return {}

if __name__ == "__main__":
    dashboard = MetricsDashboard()

    # Example: Log causal validation success
    dashboard.log_causal_validation("rule_123", success=True)

    # Example: Log AI-to-AI trust score
    dashboard.log_ai_trust_verification("What causes inflation?", consistency_score=0.95)

    # Example: Log counterfactual failures
    dashboard.log_counterfactual_failures("rule_456", failure_count=3)

    # Example: Fetch all metrics
    print("Causal Validation Metrics:", dashboard.get_causal_validation_metrics())
    print("AI Trust Verification Metrics:", dashboard.get_ai_trust_metrics())
    print("Counterfactual Failure Metrics:", dashboard.get_counterfactual_failure_metrics())

    # Example: Generate a full AI safety report
    print("Dashboard Report:", dashboard.generate_dashboard_report())

    dashboard.close()
