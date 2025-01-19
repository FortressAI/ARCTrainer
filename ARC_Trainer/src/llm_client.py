import json
from loguru import logger
import requests


class LLMClient:
    def __init__(self, config_path="config.json"):
        """
        Initializes the LLM Client with settings from a config file.

        Args:
            config_path (str): Path to the configuration file.
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            self.api_url = config["llm_client"]["api_url"]
            self.api_key = config["llm_client"]["api_key"]
            self.timeout = config["llm_client"]["timeout"]
            self.endpoints = config["endpoints"]
            logger.info("LLMClient initialized with configuration.")
        except KeyError as e:
            logger.error(f"Missing key in configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def query_llm(self, prompt):
        """
        Sends a query to the LLM and retrieves the response, ensuring it includes causal reasoning.

        Args:
            prompt (str): The input prompt to send to the LLM.

        Returns:
            dict: Response from the LLM, or an error message.
        """
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"}

            response = requests.post(
                f"{self.api_url}{self.endpoints['query']}",
                headers=headers,
                json={"prompt": self._force_causal_questioning(prompt)},
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return {"error": "API request failed", "details": response.text}

            llm_response = response.json()
            return self._validate_causal_explanation(prompt, llm_response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return {"error": "Request failed", "details": str(e)}

    def _force_causal_questioning(self, prompt):
        """
        Rewrites the prompt to enforce causal reasoning.

        Args:
            prompt (str): Original prompt.

        Returns:
            str: Modified prompt enforcing causality.
        """
        causal_prompt = f"{prompt} \n\n Please explain why this is true using clear cause-effect relationships."
        logger.info(f"Modified prompt for causal reasoning: {causal_prompt}")
        return causal_prompt

    def _validate_causal_explanation(self, prompt, response):
        """
        Validates the response to ensure it includes causal justifications.

        Args:
            prompt (str): The original prompt.
            response (dict): The LLM's response.

        Returns:
            dict: The validated response or an error message.
        """
        try:
            explanation = response.get("response", "")
            validation_query = f"Does the response '{explanation}' provide a causal explanation for '{prompt}'?"

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"}

            validation_response = requests.post(
                f"{self.api_url}{self.endpoints['validate']}",
                headers=headers,
                json={"query": validation_query},
                timeout=self.timeout
            )

            if validation_response.status_code != 200:
                logger.error(f"Validation API error: {validation_response.status_code} - {validation_response.text}")
                return {"error": "Validation failed", "response": response}

            is_causal = validation_response.json().get("valid", False)
            if not is_causal:
                logger.warning(f"LLM response lacks causal reasoning: {response}")
                return {"error": "Response lacks causal reasoning", "response": response}

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return {"error": "Validation request failed", "details": str(e)}

    def enforce_socratic_dialogue(self, prompt):
        """
        Engages in Socratic questioning to challenge AI's reasoning.

        Args:
            prompt (str): The input prompt to challenge.

        Returns:
            str: Response after being questioned for deeper reasoning.
        """
        try:
            modified_prompt = f"{prompt} \n\n Why is this the case? What would happen if the opposite were true?"
            return self.query_llm(modified_prompt)
        except Exception as e:
            logger.error(f"Error in Socratic dialogue enforcement: {e}")
            return {"error": "Failed to enforce Socratic questioning"}

    def validate_ai_to_ai_consistency(self, prompt):
        """
        Ensures multiple AI models provide consistent and causally valid responses.

        Args:
            prompt (str): The query to validate across AI models.

        Returns:
            dict: Consensus response or indication of inconsistencies.
        """
        try:
            ai_models = ["model_a", "model_b", "model_c"]
            responses = {}

            for model in ai_models:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"}

                response = requests.post(
                    f"{self.api_url}/{model}{self.endpoints['query']}",
                    headers=headers,
                    json={"prompt": prompt},
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    responses[model] = response.json().get("response", "")

            # Check for consistency
            unique_responses = set(responses.values())
            if len(unique_responses) > 1:
                logger.warning(f"Inconsistent AI-to-AI responses: {responses}")
                return {"error": "AI models disagree", "responses": responses}

            return {"response": list(unique_responses)[0]}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error validating AI-to-AI consistency: {e}")
            return {"error": "Failed AI-to-AI validation"}

if __name__ == "__main__":
    client = LLMClient(config_path="config.json")

    prompt = "What is the relationship between smoking and lung cancer?"
    llm_response = client.query_llm(prompt)
    print("LLM Response:", llm_response)

    if "error" not in llm_response:
        is_valid = client._validate_causal_explanation(prompt, llm_response)
        print("Response Validation:", is_valid)

    # Example of enforcing Socratic dialogue
    deeper_reasoning = client.enforce_socratic_dialogue("Why is democracy important?")
    print("Socratic Questioning Response:", deeper_reasoning)

    # AI-to-AI Trust Verification
    ai_validation = client.validate_ai_to_ai_consistency("How does climate change impact hurricanes?")
    print("AI-to-AI Validation Response:", ai_validation)
