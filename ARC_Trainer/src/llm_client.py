import os
from loguru import logger
from openai import OpenAI  # <-- new import from openai v1+

class LLMClient:
    def __init__(self, api_key=None):
        """
        Initializes the LLM Client to process ontology rules using the new openai>=1.0 library.

        Args:
            api_key (str, optional): OpenAI API key. 
                                     If not provided, uses environment variable: OPENAI_API_KEY
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("Missing API Key: Set OPENAI_API_KEY as an environment variable "
                         "or pass it as a parameter.")
            raise ValueError("OpenAI API Key is required.")

        # Instantiate the new 'OpenAI' client with your API key
        self.client = OpenAI(api_key=self.api_key)
        logger.info("LLMClient initialized for multi-domain ontology processing, using new openai>=1.0")

    def query_llm(self, prompt):
        """
        Sends a query to the LLM via openai>=1.0 style:
         client.chat.completions.create(...)
        Returns a dict with 'response' or 'error'.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",  # or "gpt-3.5-turbo", "gpt-4o", etc.
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            # Extract the text from the assistant's message
            result = completion.choices[0].message.content.strip()
            return {"response": result}

        except Exception as e:
            logger.error(f"Error in LLM query: {e}")
            return {"error": "LLM processing failed"}

    def convert_cnl_to_prolog(self, cnl_rule):
        """
        Converts a Controlled Natural Language (CNL) ontology rule into Prolog.

        Args:
            cnl_rule (str): Human-readable ontology rule.

        Returns:
            dict: e.g. {"response": "some Prolog rule..."}
        """
        prompt = f"Convert this Controlled Natural Language rule into Prolog: {cnl_rule}"
        return self.query_llm(prompt)

    def refine_ontology_rule(self, cnl_rule):
        """
        Uses AI to improve an existing ontology rule.

        Args:
            cnl_rule (str): Human-readable ontology rule.

        Returns:
            dict: e.g. {"response": "Improved rule..."}
        """
        prompt = f"Improve the clarity and accuracy of this ontology rule: {cnl_rule}"
        return self.query_llm(prompt)

    def cross_domain_mapping(self, domain1, domain2):
        """
        Suggests relationships between ontology concepts in two different domains.

        Args:
            domain1 (str): First ontology domain.
            domain2 (str): Second ontology domain.

        Returns:
            dict: e.g. {"response": "Some domain mappings..."}
        """
        prompt = f"Suggest ontology relationships between the domain of {domain1} and {domain2}."
        return self.query_llm(prompt)

if __name__ == "__main__":
    logger.info("Testing LLMClient with the new openai>=1.0 library...")

    llm_client = LLMClient()

    # Example: Convert CNL to Prolog for a legal rule
    cnl_rule = "A contract is a legally binding agreement between two or more parties."
    prolog_rule = llm_client.convert_cnl_to_prolog(cnl_rule)
    print("Converted Prolog Rule:", prolog_rule)

    # Example: Refine a healthcare ontology rule
    cnl_rule = "Vaccines help protect against infectious diseases."
    refined_rule = llm_client.refine_ontology_rule(cnl_rule)
    print("Refined Ontology Rule:", refined_rule)

    # Example: Suggest relationships between AI Ethics and Legal
    mapping = llm_client.cross_domain_mapping(domain1="AI Ethics", domain2="Legal")
    print("AI Ethics ↔ Legal Relationships:", mapping)
