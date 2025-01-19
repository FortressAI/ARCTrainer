from neo4j import GraphDatabase
from loguru import logger
from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split

class LanguageGameTrainer:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", model_name="bert-base-uncased"):
        """
        Initializes the Language Game Trainer with Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            model_name (str): Pretrained transformer model.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)  # 3 reasoning categories
        self.model_name = model_name
        logger.info("LanguageGameTrainer initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def fetch_language_game_data(self):
        """
        Fetches reasoning-based language game training data from Neo4j.

        Returns:
            DatasetDict: Hugging Face DatasetDict with train and validation splits.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (g:LanguageGame)
                    RETURN g.question AS question, g.answer AS answer, g.strategy AS strategy
                    """
                )

                data = [{"text": record["question"], "label": self.map_strategy_to_label(record["strategy"])} for record in result]

                if not data:
                    logger.info("No training data available for language game model updates.")
                    return

                train_texts, val_texts, train_labels, val_labels = train_test_split(
                    [d["text"] for d in data],
                    [d["label"] for d in data],
                    test_size=0.2,
                    random_state=42
                )

                train_dataset = Dataset.from_dict({"text": train_texts, "label": train_labels})
                val_dataset = Dataset.from_dict({"text": val_texts, "label": val_labels})

                datasets = DatasetDict({"train": train_dataset, "validation": val_dataset})

                logger.info(f"Fetched {len(train_texts)} training examples.")
                return datasets

        except Exception as e:
            logger.error(f"Error fetching language game training data: {e}")
            raise

    def preprocess_data(self, dataset):
        """
        Tokenizes the dataset for training.

        Args:
            dataset (DatasetDict): DatasetDict containing train and validation splits.

        Returns:
            DatasetDict: Tokenized dataset.
        """
        try:
            tokenized_dataset = dataset.map(lambda x: self.tokenizer(x["text"], padding="max_length", truncation=True), batched=True)
            logger.info("Data tokenized successfully.")
            return tokenized_dataset
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise

    def train_model(self, tokenized_data):
        """
        Fine-tunes the model using the tokenized dataset.

        Args:
            tokenized_data (DatasetDict): Tokenized dataset with train and validation splits.

        Returns:
            dict: Training metrics.
        """
        try:
            training_args = TrainingArguments(
                output_dir="./models/language_game",
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
                train_dataset=tokenized_data["train"],
                eval_dataset=tokenized_data["validation"],
                tokenizer=self.tokenizer,
            )

            logger.info("Starting language game model training...")
            train_result = trainer.train()
            trainer.save_model(training_args.output_dir)
            logger.info(f"Language game model updated and saved to {training_args.output_dir}.")

            return train_result.metrics

        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise

    def map_strategy_to_label(self, strategy):
        """
        Maps reasoning strategies to numerical labels.

        Args:
            strategy (str): Reasoning strategy label from training data.

        Returns:
            int: Numerical label.
        """
        strategy_map = {
            "socratic_questioning": 0,
            "logical_deduction": 1,
            "ethical_reasoning": 2
        }
        return strategy_map.get(strategy, 2)

    def validate_language_game(self, question, user_answer):
        """
        Validates an AI-generated response using stored reasoning strategies.

        Args:
            question (str): The question posed.
            user_answer (str): The AI's response.

        Returns:
            bool: True if the answer follows a known valid reasoning strategy, False otherwise.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (g:LanguageGame {question: $question})
                    RETURN g.strategy AS expected_strategy
                    """,
                    question=question
                )

                record = result.single()
                if record and record["expected_strategy"]:
                    valid = self.check_reasoning_alignment(user_answer, record["expected_strategy"])
                    logger.info(f"Validation result for '{question}': {valid}")
                    return valid

                return False
        except Exception as e:
            logger.error(f"Error validating language game response: {e}")
            return False

    def check_reasoning_alignment(self, response, expected_strategy):
        """
        Checks if the response aligns with the expected reasoning strategy.

        Args:
            response (str): AI response to validate.
            expected_strategy (str): Expected reasoning approach.

        Returns:
            bool: True if aligned, False otherwise.
        """
        # Simulated validation logic (can be replaced with NLP-based evaluation)
        if expected_strategy == "socratic_questioning" and "why" in response.lower():
            return True
        elif expected_strategy == "logical_deduction" and "therefore" in response.lower():
            return True
        elif expected_strategy == "ethical_reasoning" and "should" in response.lower():
            return True
        return False

if __name__ == "__main__":
    trainer = LanguageGameTrainer(uri="bolt://localhost:7687", user="neo4j", password="password")

    # Example: Fetch and preprocess training data
    dataset = trainer.fetch_language_game_data()
    tokenized_data = trainer.preprocess_data(dataset)

    # Example: Train model
    metrics = trainer.train_model(tokenized_data)
    logger.info(f"Training metrics: {metrics}")

    # Example: Validate AI reasoning
    is_valid = trainer.validate_language_game("Should we increase minimum wage?", "Why do you believe it helps society?")
    print("Reasoning Validation:", is_valid)

    trainer.close()
