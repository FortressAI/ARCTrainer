from loguru import logger
from neo4j import GraphDatabase
import random
from src.llm_client import LLM  # Uses LLM for Socratic questioning & counterfactuals

class CounterexampleFinder:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, num_simulations=1000):
        """
        Initializes the counterexample finder with Monte Carlo integration and Neo4j support.
        Args:
            neo4j_uri (str): URI for connecting to Neo4j.
            neo4j_user (str): Username for Neo4j authentication.
            neo4j_password (str): Password for Neo4j authentication.
            num_simulations (int): Number of Monte Carlo iterations for probabilistic rule evaluation.
        """
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.num_simulations = num_simulations
        logger.info("CounterexampleFinder initialized with Monte Carlo reasoning and fairness validation.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def find_counterexample(self, rule):
        """
        Generates counterexamples using Socratic questioning, Monte Carlo counterfactuals, and fairness validation.
        """
        logger.info(f"Generating counterexamples for rule: {rule}")
        counterexamples = self.generate_diverse_cases(rule)

        valid_examples = []
        for example in counterexamples:
            if self.violates_fairness(example):
                logger.warning(f"Counterexample {example} fails fairness constraint.")
                self.log_failure(example, "Fails fairness constraint")
                continue

            # Socratic Questioning: AI must justify this rule before acceptance
            justification = self.ask_socratic_question(rule, example)
            if not self.valid_causal_chain(justification):
                logger.warning(f"Counterexample {example} lacks valid causal reasoning.")
                self.log_failure(example, "Fails Socratic reasoning check")
                continue

            # Monte Carlo Counterfactual Testing
            confidence_score = self.monte_carlo_counterfactual(rule)
            if confidence_score < 0.7:  # Threshold for rule acceptance
                logger.warning(f"Rule {rule} failed Monte Carlo reasoning with confidence {confidence_score}.")
                self.log_failure(example, "Fails Monte Carlo counterfactual validation")
                continue

            valid_examples.append(example)

        return valid_examples

    def monte_carlo_counterfactual(self, rule):
        """
        Runs Monte Carlo simulations to generate counterfactual reasoning probabilities.
        Returns:
            float: Confidence score (0 to 1) for the rule’s validity across scenarios.
        """
        successful_cases = 0
        for _ in range(self.num_simulations):
            counterfactual = self.generate_random_variation(rule)
            if self.valid_causal_chain(counterfactual):
                successful_cases += 1
        return successful_cases / self.num_simulations  # Probability of correctness

    def generate_random_variation(self, rule):
        """Creates a stochastic variation of the rule for counterfactual testing."""
        query = f"Generate a randomized version of the rule '{rule}' for counterfactual testing."
        return LLM.ask(query)

    def ask_socratic_question(self, rule, example):
        """
        Uses Socratic questioning to force AI to justify a rule.
        """
        query = f"Why does {rule} hold in the case of {example}? Provide a causal justification."
        return LLM.ask(query)

    def valid_causal_chain(self, explanation):
        """Determines if an explanation follows valid causal logic."""
        query = f"Does this explanation follow a sound causal chain? {explanation}"
        result = LLM.ask(query)
        return "valid" in result.lower()

    def violates_fairness(self, example):
        """
        Checks if a counterexample reveals a biased outcome.
        """
        query = f"Does this rule, as applied to {example}, introduce any bias?"
        return "yes" in LLM.ask(query).lower()

    def log_failure(self, example, reason):
        """
        Stores failing counterexamples in Neo4j for analysis.
        """
        logger.info(f"Logging failed counterexample: {example} | Reason: {reason}")
        with self.driver.session() as session:
            query = """
            MERGE (c:Counterexample {example: $example})
            SET c.failure_reason = $reason
            """
            session.run(query, example=example, reason=reason)
