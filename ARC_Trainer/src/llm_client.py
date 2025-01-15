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
            self.endpoints = config["llm_client"]["endpoints"]
            logger.info("LLMClient initialized with configuration.")
        except KeyError as e:
            logger.error(f"Missing key in configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def query_llm(self, prompt):
        """
        Sends a query to the LLM and retrieves the response.

        Args:
            prompt (str): The input prompt to send to the LLM.

        Returns:
            dict: Response from the LLM, or an error message.
        """
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.api_url}{self.endpoints['query']}",
                headers=headers,
                json={"prompt": prompt},
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return {"error": "API request failed", "details": response.text}

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return {"error": "Request failed", "details": str(e)}

    def validate_response(self, prompt, response):
        """
        Validates a response from the LLM against the original prompt.

        Args:
            prompt (str): The original prompt.
            response (str): The LLM's response to validate.

        Returns:
            bool: True if the response is valid, False otherwise.
        """
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            validation_response = requests.post(
                f"{self.api_url}{self.endpoints['validate']}",
                headers=headers,
                json={"prompt": prompt, "response": response},
                timeout=self.timeout
            )

            if validation_response.status_code != 200:
                logger.error(
                    f"Validation API error: {validation_response.status_code} - {validation_response.text}"
                )
                return False

            return validation_response.json().get("valid", False)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    client = LLMClient(config_path="config.json")

    prompt = "What is the capital of France?"
    llm_response = client.query_llm(prompt)
    print("LLM Response:", llm_response)

    if "error" not in llm_response:
        is_valid = client.validate_response(prompt, llm_response.get("response"))
        print("Response Validation:", is_valid)
