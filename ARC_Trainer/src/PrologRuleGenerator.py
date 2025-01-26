import pyswip
from loguru import logger
from src.llm_client import LLMClient

class PrologRuleGenerator:
    def __init__(self, prolog_path="prolog_engine.pl"):
        """
        Initializes the Prolog Rule Generator for ontology validation.

        Args:
            prolog_path (str): Path to the Prolog rule file.
        """
        self.prolog = pyswip.Prolog()
        self.llm_client = LLMClient()

        try:
            self.prolog.consult(prolog_path)
            logger.info(f"Prolog engine initialized with rules from {prolog_path}.")
        except Exception as e:
            logger.error(f"Error loading Prolog file: {e}")

    def generate_prolog_rule(self, cnl_rule):
        """
        Converts a Controlled Natural Language (CNL) rule into Prolog.

        Args:
            cnl_rule (str): Human-readable ontology rule.

        Returns:
            dict: Converted Prolog rule.
        """
        prolog_rule = self.llm_client.convert_cnl_to_prolog(cnl_rule)
        return prolog_rule

    def validate_rule_against_test_cases(self, prolog_rule, test_cases):
        """
        Validates a Prolog rule against provided test cases.

        Args:
            prolog_rule (str): Prolog rule to validate.
            test_cases (list): List of test cases.

        Returns:
            bool: True if all test cases pass, False otherwise.
        """
        try:
            self.prolog.assertz(prolog_rule)

            for test_case in test_cases:
                result = list(self.prolog.query(test_case))
                if not result:
                    logger.warning(f"Validation failed for test case: {test_case}")
                    return False

            logger.info("Prolog rule validation passed all test cases.")
            return True

        except Exception as e:
            logger.error(f"Error validating Prolog rule: {e}")
            return False

    def generate_counterexample(self, prolog_rule):
        """
        Generates a counterexample where the Prolog rule might fail.

        Args:
            prolog_rule (str): Prolog rule to test.

        Returns:
            dict: Counterexample details.
        """
        try:
            self.prolog.assertz(prolog_rule)

            # Ask the AI to generate a potential counterexample
            counterexample_prompt = f"Find a counterexample for this Prolog rule: {prolog_rule}"
            counterexample = self.llm_client.query_llm(counterexample_prompt)

            if counterexample["response"]:
                logger.warning(f"Counterexample found: {counterexample['response']}")
                return {"status": "counterexample_found", "example": counterexample["response"]}
            else:
                return {"status": "no_counterexample"}

        except Exception as e:
            logger.error(f"Error generating counterexample: {e}")
            return {"error": "Counterexample generation failed"}

if __name__ == "__main__":
    logger.info("Initializing Prolog Rule Generator")

    prolog_generator = PrologRuleGenerator()

    # Example: Convert a legal CNL rule into Prolog
    cnl_rule = "A contract is a legally binding agreement between two or more parties."
    prolog_rule = prolog_generator.generate_prolog_rule(cnl_rule)
    print("Generated Prolog Rule:", prolog_rule)

    # Example: Validate a healthcare Prolog rule
    healthcare_prolog_rule = "vaccine(X) :- preventive_treatment(X), protects_against(infectious_diseases)."
    test_cases = ["vaccine(covid19_vaccine)."]
    validation_result = prolog_generator.validate_rule_against_test_cases(healthcare_prolog_rule, test_cases)
    print("Validation Result:", validation_result)

    # Example: Generate a counterexample for an AI Ethics rule
    ai_ethics_prolog_rule = "data_privacy(X) :- ensures(user_control(X)), prevents(unauthorized_access(X))."
    counterexample = prolog_generator.generate_counterexample(ai_ethics_prolog_rule)
    print("Counterexample:", counterexample)
