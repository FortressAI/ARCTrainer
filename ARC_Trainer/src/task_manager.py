from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from loguru import logger
import uuid
from llm_client import LLMClient
from prolog_rule_generator import PrologRuleGenerator
from learning_agent import LearningAgent

app = Flask(__name__)

class TaskManager:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Task Manager with Neo4j and Prolog integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.llm_client = LLMClient()
        self.prolog_generator = PrologRuleGenerator()
        self.learning_agent = LearningAgent()

        logger.info("TaskManager initialized with multi-domain ontology support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def submit_task(self, task_data):
        """
        Submits a new ontology rule to the system.

        Args:
            task_data (dict): Contains ontology rule details.

        Returns:
            dict: Task ID and status.
        """
        try:
            task_id = str(uuid.uuid4())
            cnl_rule = task_data.get("cnl_rule")
            domain = task_data.get("domain")

            if not cnl_rule or not domain:
                return {"error": "Missing ontology rule or domain."}

            # Convert CNL rule to Prolog
            prolog_response = self.llm_client.query_llm(f"Convert this into Prolog: {cnl_rule}")
            prolog_rule = prolog_response.get("response")

            if not prolog_rule:
                logger.warning("Failed to generate Prolog rule from CNL.")
                return {"error": "Ontology rule conversion failed"}

            # Validate & Store the rule
            validation_result = self.learning_agent.validate_and_store_rule(cnl_rule, domain)
            if "error" in validation_result:
                return validation_result

            # Store the task metadata
            with self.driver.session() as session:
                session.run(
                    """
                    CREATE (t:Task {id: $task_id, status: 'queued', cnl_rule: $cnl_rule, prolog_rule: $prolog_rule, domain: $domain})
                    """,
                    task_id=task_id, cnl_rule=cnl_rule, prolog_rule=prolog_rule, domain=domain
                )

            logger.info(f"Task {task_id} submitted successfully for domain '{domain}'.")
            return {"task_id": task_id, "status": "queued", "prolog_rule": prolog_rule}

        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            return {"error": "Failed to submit ontology rule"}

    def get_task_status(self, task_id):
        """
        Retrieves the status and metadata of a submitted ontology task.

        Args:
            task_id (str): Task ID.

        Returns:
            dict: Task status and metadata.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    RETURN t.status AS status, t.cnl_rule AS cnl_rule, t.prolog_rule AS prolog_rule, t.domain AS domain
                    """,
                    task_id=task_id
                )

                record = result.single()
                if record:
                    logger.info(f"Task {task_id} status retrieved.")
                    return {
                        "status": record["status"],
                        "cnl_rule": record["cnl_rule"],
                        "prolog_rule": record["prolog_rule"],
                        "domain": record["domain"]
                    }
                else:
                    return {"error": "Task not found"}

        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            return {"error": "Internal server error"}

    def validate_ontology_rule(self, rule):
        """
        Validates an ontology rule before storage.

        Args:
            rule (str): Prolog rule to validate.

        Returns:
            dict: Validation status.
        """
        try:
            validation_result = self.prolog_generator.validate_rule_against_test_cases(rule, [])

            if validation_result:
                return {"status": "valid"}
            else:
                return {"status": "invalid", "error": "Rule did not pass validation"}

        except Exception as e:
            logger.error(f"Ontology validation failed: {e}")
            return {"error": "Validation error"}

@app.route("/tasks", methods=["POST"])
def submit_task():
    """
    API endpoint to submit an ontology rule.
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
    API endpoint to retrieve the status of a submitted ontology task.
    """
    try:
        manager = TaskManager()
        response = manager.get_task_status(task_id)
        manager.close()
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in get_task_status endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/validate_rule", methods=["POST"])
def validate_rule():
    """
    API endpoint to validate an ontology rule.
    """
    try:
        data = request.json
        rule = data.get("rule")

        if not rule:
            return jsonify({"error": "Rule is required"}), 400

        manager = TaskManager()
        response = manager.validate_ontology_rule(rule)
        manager.close()
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in validate_rule endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Task Manager API")
    app.run(host="0.0.0.0", port=5002)
