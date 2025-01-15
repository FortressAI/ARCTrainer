from neo4j import GraphDatabase
from loguru import logger
from pyswip import Prolog

class CounterexampleFinder:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", prolog_files=[]):
        """
        Initializes the Counterexample Finder with Prolog and Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            prolog_files (list): List of Prolog files to load for reasoning and validation.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.prolog = Prolog()

        # Load Prolog rules
        for file in prolog_files:
            try:
                self.prolog.consult(file)
                logger.info(f"Loaded Prolog file: {file}")
            except Exception as e:
                logger.error(f"Failed to load Prolog file {file}: {e}")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def find_counterexamples(self, rule, domain_examples):
        """
        Identifies counterexamples that fail a given rule within a specified domain.

        Args:
            rule (str): The Prolog rule to test.
            domain_examples (list): List of examples in the form of input/output pairs.

        Returns:
            list: Counterexamples that fail the rule.
        """
        try:
            self.prolog.assertz(rule)
            logger.info(f"Asserting rule for counterexample testing: {rule}")

            counterexamples = []

            for example in domain_examples:
                input_data = example["input"]
                expected_output = example["expected_output"]
                query = f"{rule.split('(')[0]}({input_data}, Result)"

                try:
                    result = list(self.prolog.query(query))
                    if not result or result[0]["Result"] != expected_output:
                        counterexamples.append({
                            "input": input_data,
                            "expected": expected_output,
                            "actual": result[0]["Result"] if result else None
                        })
                except Exception as e:
                    logger.error(f"Error executing query for input {input_data}: {e}")

            self.prolog.retract(rule)
            logger.info("Retracted rule after counterexample testing.")
            return counterexamples

        except Exception as e:
            logger.error(f"Error finding counterexamples: {e}")
            self.prolog.retract(rule)
            return []

    def store_counterexamples(self, rule_id, counterexamples):
        """
        Store identified counterexamples in Neo4j for future reference.

        Args:
            rule_id (str): Unique identifier for the rule.
            counterexamples (list): Counterexamples to store.
        """
        try:
            with self.driver.session() as session:
                for counterexample in counterexamples:
                    session.run(
                        """
                        MERGE (r:Rule {id: $rule_id})
                        CREATE (ce:Counterexample {input: $input, expected: $expected, actual: $actual})
                        MERGE (r)-[:HAS_COUNTEREXAMPLE]->(ce)
                        """,
                        rule_id=rule_id,
                        input=counterexample["input"],
                        expected=counterexample["expected"],
                        actual=counterexample["actual"]
                    )
                logger.info(f"Stored counterexamples for rule {rule_id} in Neo4j.")
        except Exception as e:
            logger.error(f"Error storing counterexamples: {e}")

if __name__ == "__main__":
    # Example usage
    logger.info("Initializing Counterexample Finder")

    finder = CounterexampleFinder(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        prolog_files=["./prolog_rules/geometry_rules.pl"]
    )

    test_rule = "double(X, Y) :- Y is X * 2."
    examples = [
        {"input": "2", "expected_output": "4"},
        {"input": "3", "expected_output": "6"},
        {"input": "4", "expected_output": "10"}  # Incorrect example to test counterexamples
    ]

    counterexamples = finder.find_counterexamples(test_rule, examples)
    if counterexamples:
        rule_id = str(hash(test_rule))
        finder.store_counterexamples(rule_id, counterexamples)
        logger.warning(f"Counterexamples found: {counterexamples}")
    else:
        logger.info("No counterexamples found. Rule validated.")

    finder.close()