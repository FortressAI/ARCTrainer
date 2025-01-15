from neo4j import GraphDatabase
from loguru import logger
from pyswip import Prolog

class PrologRuleGenerator:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", prolog_files=[]):
        """
        Initializes the Prolog Rule Generator with existing Prolog rules and Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            prolog_files (list): List of Prolog files to load for rule validation.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.prolog = Prolog()

        # Load existing Prolog rules
        for file in prolog_files:
            try:
                self.prolog.consult(file)
                logger.info(f"Loaded Prolog file: {file}")
            except Exception as e:
                logger.error(f"Failed to load Prolog file {file}: {e}")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def propose_rule_from_existing(self, reasoning_trace):
        """
        Propose a new rule by leveraging existing Prolog rules and reasoning traces.

        Args:
            reasoning_trace (dict): Reasoning trace containing task details and inferred logic.

        Returns:
            str: Proposed Prolog rule based on existing rules and reasoning.
        """
        try:
            task_id = reasoning_trace.get("task_id")
            inferred_logic = reasoning_trace.get("inferred_logic")

            if not inferred_logic:
                raise ValueError("No inferred logic provided in reasoning trace.")

            rule = f"{inferred_logic}"
            logger.info(f"Proposed rule for task {task_id}: {rule}")
            return rule

        except Exception as e:
            logger.error(f"Error proposing rule: {e}")
            raise

    def validate_rule_against_test_cases(self, rule, test_cases):
        """
        Validate a proposed rule using test cases against the loaded Prolog rules.

        Args:
            rule (str): Proposed Prolog rule.
            test_cases (list): List of test cases with input/output pairs.

        Returns:
            bool: True if the rule passes all test cases, False otherwise.
        """
        try:
            # Temporarily assert the rule in Prolog
            self.prolog.assertz(rule)
            logger.info(f"Asserting rule for validation: {rule}")

            for test_case in test_cases:
                input_data = test_case["input"]
                expected_output = test_case["output"]
                query = f"{rule.split('(')[0]}({input_data}, Result)"

                try:
                    result = list(self.prolog.query(query))
                    if not result or result[0]["Result"] != expected_output:
                        self.prolog.retract(rule)
                        logger.warning(f"Rule validation failed for input: {input_data}")
                        return False
                except Exception as e:
                    logger.error(f"Error executing query for input {input_data}: {e}")
                    self.prolog.retract(rule)
                    return False

            self.prolog.retract(rule)
            logger.info("Rule validated successfully.")
            return True

        except Exception as e:
            logger.error(f"Error validating rule: {e}")
            self.prolog.retract(rule)
            return False

    def store_valid_rule(self, rule_id, rule):
        """
        Store a validated rule in Neo4j.

        Args:
            rule_id (str): Unique identifier for the rule.
            rule (str): The Prolog rule to store.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (r:Rule {id: $rule_id, definition: $rule})
                    """,
                    rule_id=rule_id,
                    rule=rule
                )
                logger.info(f"Stored rule {rule_id} in Neo4j.")
        except Exception as e:
            logger.error(f"Error storing rule {rule_id}: {e}")

if __name__ == "__main__":
    logger.info("Initializing Prolog Rule Generator")

    generator = PrologRuleGenerator(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        prolog_files=["./prolog_rules/geometry_rules.pl"]
    )

    reasoning_trace = {
        "task_id": "example_task",
        "inferred_logic": "double(X, Y) :- Y is X * 2."
    }

    proposed_rule = generator.propose_rule_from_existing(reasoning_trace)
    test_cases = [
        {"input": "2", "output": "4"},
        {"input": "3", "output": "6"},
        {"input": "4", "output": "8"}
    ]

    if generator.validate_rule_against_test_cases(proposed_rule, test_cases):
        rule_id = str(hash(proposed_rule))
        generator.store_valid_rule(rule_id, proposed_rule)
    else:
        logger.warning("Proposed rule validation failed.")

    generator.close()
