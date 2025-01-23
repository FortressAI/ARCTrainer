from loguru import logger
from neo4j import GraphDatabase
from llm_client import LLM  # Uses LLM for near-enemy detection

class CounterexampleFinder:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        """
        Initializes the counterexample finder with Neo4j integration.
        """
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def find_counterexample(self, rule):
        """
        Generates counterexamples using Socratic questioning and counterfactual reasoning.
        AI must justify its reasoning causally before accepting the rule.
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

            # Near Enemy Check: Is this rule deceptive?
            if self.is_near_enemy(rule):
                logger.warning(f"Rule {rule} may be a near enemy.")
                self.log_failure(example, "Fails near enemy detection")
                continue

            valid_examples.append(example)

        return valid_examples

    def is_near_enemy(self, rule):
        """
        Uses LLM to detect if a rule appears valid but subtly undermines logic or fairness.
        """
        query = f"Does the rule '{rule}' appear logically sound but introduce bias or deception?"
        return "yes" in LLM.ask(query).lower()

    def generate_diverse_cases(self, rule):
        """
        Uses LLM to generate diverse counterexamples that challenge different aspects of a rule.
        """
        query = f"Generate multiple counterexamples that challenge the logic of the rule: {rule}"
        return LLM.ask(query)

    def ask_socratic_question(self, rule, example):
        """
        Forces AI to justify a rule using Socratic questioning.
        """
        query = f"Why does {rule} hold in the case of {example}? Provide a causal justification."
        return LLM.ask(query)

    def valid_causal_chain(self, explanation):
        """
        Determines if an explanation follows valid causal logic.
        """
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
