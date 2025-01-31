import json
import os
from loguru import logger
import requests
from neo4j import GraphDatabase
from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split

class LLMClientIntent:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="mysecurepassword", api_url="http://localhost:8000/api/intent", model_name="bert-base-uncased"):
        """
        Initializes the LLM Intent Client with Neo4j and a fine-tuned model.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            api_url (str): Base URL for the intent detection API.
            model_name (str): Pretrained transformer model.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.api_url = api_url
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=5)  # 5 intent categories
        self.model_name = model_name
        logger.info("LLMClientIntent initialized with model.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def analyze_intent(self, input_text):
        """
        Analyzes the intent of the given input text using an external API.

        Args:
            input_text (str): Text input for intent detection.

        Returns:
            dict: Parsed intent data, including intent type and confidence score.
        """
        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={"text": input_text}
            )

            if response.status_code != 200:
                logger.error(f"Intent detection API error: {response.status_code} - {response.text}")
                return {"error": "Intent API request failed"}

            intent_data = response.json()
            logger.info(f"Intent analysis result: {intent_data}")

            # Store the detected intent in Neo4j
            self.store_intent_data(input_text, intent_data)
            
            return intent_data

        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {"error": "Unable to analyze intent"}

    def store_intent_data(self, user_input, intent_data):
        """
        Stores the detected intent and confidence score in the knowledge graph.

        Args:
            user_input (str): The original user query.
            intent_data (dict): The intent classification result.
        """
        try:
            intent_type = intent_data.get("intent", "unknown")
            confidence = intent_data.get("confidence", 0.0)

            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (i:Intent {text: $user_input})
                    SET i.intent_type = $intent_type, i.confidence = $confidence
                    """,
                    user_input=user_input,
                    intent_type=intent_type,
                    confidence=confidence
                )
                logger.info(f"Stored intent data: '{user_input}' → {intent_type} (Confidence: {confidence})")

        except Exception as e:
            logger.error(f"Error storing intent data: {e}")

    def retrieve_intent_data(self, user_input):
        """
        Retrieves past intent classifications for a given user input.

        Args:
            user_input (str): The original user query.

        Returns:
            dict: Retrieved intent data or an empty result.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (i:Intent {text: $user_input})
                    RETURN i.intent_type AS intent, i.confidence AS confidence
                    """,
                    user_input=user_input
                )

                record = result.single()
                if record:
                    logger.info(f"Retrieved intent data for '{user_input}': {record}")
                    return {"intent": record["intent"], "confidence": record["confidence"]}
                else:
                    logger.warning(f"No past intent data found for '{user_input}'.")
                    return {}

        except Exception as e:
            logger.error(f"Error retrieving intent data: {e}")
            return {}

    def update_intent_model(self):
        """
        Updates the intent recognition model using past user interactions stored in Neo4j.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (i:Intent)
                    RETURN i.text AS text, i.intent_type AS intent
                    """
                )

                training_data = [{"text": record["text"], "intent": record["intent"]} for record in result]

                if not training_data:
                    logger.info("No training data available for intent model updates.")
                    return

                # Convert data into Hugging Face Dataset format
                train_texts, val_texts, train_labels, val_labels = train_test_split(
                    [d["text"] for d in training_data], 
                    [self.map_intent_to_label(d["intent"]) for d in training_data], 
                    test_size=0.2, 
                    random_state=42
                )

                train_dataset = Dataset.from_dict({"text": train_texts, "label": train_labels})
                val_dataset = Dataset.from_dict({"text": val_texts, "label": val_labels})

                datasets = DatasetDict({"train": train_dataset, "validation": val_dataset})

                # Tokenize the datasets
                tokenized_datasets = datasets.map(lambda x: self.tokenizer(x["text"], padding="max_length", truncation=True), batched=True)

                training_args = TrainingArguments(
                    output_dir="./models/intent_model",
                    evaluation_strategy="epoch",
                    learning_rate=2e-5,
                    per_device_train_batch_size=16,
                    per_device_eval_batch_size=16,
                    num_train_epochs=3,
                    weight_decay=0.01,
                    save_total_limit=2,
                    logging_dir="./models/logs",
                    logging_steps=10,
                    save_strategy="epoch",
                    load_best_model_at_end=True,
                )

                trainer = Trainer(
                    model=self.model,
                    args=training_args,
                    train_dataset=tokenized_datasets["train"],
                    eval_dataset=tokenized_datasets["validation"],
                    tokenizer=self.tokenizer,
                )

                logger.info("Starting intent model training...")
                trainer.train()
                trainer.save_model(training_args.output_dir)
                logger.info(f"Intent model updated and saved to {training_args.output_dir}.")

        except Exception as e:
            logger.error(f"Error updating intent model: {e}")

    def map_intent_to_label(self, intent):
        """
        Maps intent strings to numerical labels.

        Args:
            intent (str): Intent label from training data.

        Returns:
            int: Numerical label.
        """
        intent_map = {
            "question": 0,
            "command": 1,
            "statement": 2,
            "confirmation": 3,
            "other": 4
        }
        return intent_map.get(intent, 4)

if __name__ == "__main__":
    client = LLMClientIntent(uri="bolt://localhost:7687", user="neo4j", password="password")

    # Example: Analyze an intent
    result = client.analyze_intent("How does inflation affect housing prices?")
    print("Intent Analysis Result:", result)

    # Example: Retrieve past intent data
    past_data = client.retrieve_intent_data("How does inflation affect housing prices?")
    print("Retrieved Intent Data:", past_data)

    # Example: Update the intent model with stored interactions
    client.update_intent_model()

    client.close()
