import json
from loguru import logger
import requests

class LLMClientIntent:
    def __init__(self, api_url="http://localhost:8000/api/intent", api_key=None):
        """
        Initializes the LLM Intent Client.

        Args:
            api_url (str): The base URL of the Intent Detection API.
            api_key (str): Optional API key for authentication.
        """
        self.api_url = api_url
        self.api_key = api_key
        logger.info("LLMClientIntent initialized.")

    def analyze_intent(self, input_text):
        """
        Analyzes the intent of the given input text.

        Args:
            input_text (str): Text input for intent detection.

        Returns:
            dict: Parsed intent data, including intent type and confidence.
        """
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                self.api_url,
                headers=headers,
                json={"text": input_text},
            )

            if response.status_code != 200:
                logger.error(f"Intent Detection API error: {response.status_code} - {response.text}")
                return {"error": "Intent API request failed."}

            intent_data = response.json()
            logger.info(f"Intent analysis result: {intent_data}")
            return intent_data

        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {"error": "Unable to analyze intent."}

if __name__ == "__main__":
    # Example usage
    client = LLMClientIntent(api_url="http://localhost:8000/api/intent")

    input_text = "Can you solve this grid task?"
    result = client.analyze_intent(input_text)
    print("Intent Analysis Result:", result)
