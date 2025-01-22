from flask import Flask, jsonify
from neo4j import GraphDatabase
from loguru import logger
import redis

app = Flask(__name__)

class MetricsDashboard:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", redis_host="localhost", redis_port=6379):
        """
        Initializes the Metrics Dashboard.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            redis_host (str): Redis server hostname.
            redis_port (int): Redis server port.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

        logger.info("MetricsDashboard initialized for multi-domain ontology tracking.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def track_ontology_updates(self):
        """
        Tracks the number of ontology rules updated per domain.

        Returns:
            dict: Count of updates per domain.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:OntologyRule)
                    RETURN r.domain AS domain, COUNT(r) AS total_rules
                    """
                )
                domain_updates = {record["domain"]: record["total_rules"] for record in result}

                self.redis.set("ontology_updates", str(domain_updates))
                logger.info(f"Ontology updates tracked: {domain_updates}")

                return domain_updates
        except Exception as e:
            logger.error(f"Error tracking ontology updates: {e}")
            return {"error": "Failed to retrieve ontology update metrics"}

    def track_feedback_activity(self):
        """
        Tracks user feedback activity by domain.

        Returns:
            dict: Count of processed and pending feedback per domain.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (f:Feedback)
                    RETURN f.domain AS domain, COUNT(f) AS total_feedback, 
                           SUM(CASE WHEN f.status = 'processed' THEN 1 ELSE 0 END) AS processed,
                           SUM(CASE WHEN f.status = 'pending' THEN 1 ELSE 0 END) AS pending
                    """
                )
                feedback_activity = {record["domain"]: {"total": record["total_feedback"], 
                                                        "processed": record["processed"], 
                                                        "pending": record["pending"]} 
                                     for record in result}

                self.redis.set("feedback_activity", str(feedback_activity))
                logger.info(f"Feedback activity tracked: {feedback_activity}")

                return feedback_activity
        except Exception as e:
            logger.error(f"Error tracking feedback activity: {e}")
            return {"error": "Failed to retrieve feedback metrics"}

    def track_rule_validation_results(self):
        """
        Tracks the number of validated ontology rules and failed validations.

        Returns:
            dict: Validation pass and fail count per domain.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:OntologyRule)
                    RETURN r.domain AS domain, 
                           SUM(CASE WHEN r.validated = true THEN 1 ELSE 0 END) AS validated,
                           SUM(CASE WHEN r.validated = false THEN 1 ELSE 0 END) AS failed
                    """
                )
                validation_results = {record["domain"]: {"validated": record["validated"], 
                                                         "failed": record["failed"]} 
                                      for record in result}

                self.redis.set("rule_validations", str(validation_results))
                logger.info(f"Rule validation results tracked: {validation_results}")

                return validation_results
        except Exception as e:
            logger.error(f"Error tracking rule validation results: {e}")
            return {"error": "Failed to retrieve rule validation metrics"}

    def get_dashboard_metrics(self):
        """
        Retrieves the latest stored metrics from Redis.

        Returns:
            dict: Latest stored ontology metrics.
        """
        try:
            ontology_updates = eval(self.redis.get("ontology_updates") or "{}")
            feedback_activity = eval(self.redis.get("feedback_activity") or "{}")
            rule_validations = eval(self.redis.get("rule_validations") or "{}")

            dashboard_metrics = {
                "ontology_updates": ontology_updates,
                "feedback_activity": feedback_activity,
                "rule_validations": rule_validations
            }

            logger.info("Dashboard metrics retrieved successfully.")
            return dashboard_metrics
        except Exception as e:
            logger.error(f"Error retrieving dashboard metrics: {e}")
            return {"error": "Failed to retrieve dashboard metrics"}

@app.route("/metrics", methods=["GET"])
def get_metrics():
    """
    API endpoint to fetch all ontology tracking metrics.
    """
    try:
        manager = MetricsDashboard()
        response = manager.get_dashboard_metrics()
        manager.close()
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in get_metrics endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Metrics Dashboard API")
    app.run(host="0.0.0.0", port=5004)
