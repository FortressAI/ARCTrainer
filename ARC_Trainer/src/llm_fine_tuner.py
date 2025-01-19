import os
import json
from loguru import logger
from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset, DatasetDict
from neo4j import GraphDatabase

class LLMFineTuner:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", model_name="bert-base-uncased"):
        """
        Initializes the LLM Fine-Tuner with model, data paths, and Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            model_name (str): Pretrained model name or path.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=2)
        logger.info("LLMFineTuner initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def fetch_training_data(self):
        """
        Fetches training and validation data from Neo4j based on user feedback.

        Returns:
            DatasetDict: Hugging Face DatasetDict with train and validation splits.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (f:Feedback)
                    RETURN f.feedback AS feedback, f.rating AS rating, f.correction AS correction
                    """
                )

                train_data = []
                val_data = []
                for record in result:
                    text = record["feedback"]
                    label = 1 if record["rating"] >= 4 else 0  # High ratings = positive example
                    correction = record["correction"]

                    train_data.append({"text": text, "label": label})
                    if correction:
                        val_data.append({"text": correction, "label": 1})  # Corrections as valid responses

                train_dataset = Dataset.from_list(train_data)
                val_dataset = Dataset.from_list(val_data)

                logger.info(f"Fetched {len(train_data)} training examples.")
                logger.info(f"Fetched {len(val_data)} validation examples.")

                return DatasetDict({"train": train_dataset, "validation": val_dataset})
        except Exception as e:
            logger.error(f"Error fetching training data: {e}")
            raise

    def preprocess_data(self, dataset):
        """
        Tokenizes the dataset for the LLM.

        Args:
            dataset (DatasetDict): DatasetDict containing train and validation splits.

        Returns:
            DatasetDict: Tokenized dataset.
        """
        try:
            def tokenize_function(example):
                return self.tokenizer(example["text"], padding="max_length", truncation=True)

            tokenized_dataset = dataset.map(tokenize_function, batched=True)
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
                output_dir="./models/fine_tuned",
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

            logger.info("Starting model training...")
            train_result = trainer.train()
            logger.info("Model training completed.")

            trainer.save_model(training_args.output_dir)
            logger.info(f"Model saved to {training_args.output_dir}.")

            return train_result.metrics

        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise

if __name__ == "__main__":
    logger.info("Initializing LLM Fine-Tuner")

    fine_tuner = LLMFineTuner(uri="bolt://localhost:7687", user="neo4j", password="password")

    dataset = fine_tuner.fetch_training_data()
    tokenized_data = fine_tuner.preprocess_data(dataset)
    metrics = fine_tuner.train_model(tokenized_data)

    logger.info(f"Training metrics: {metrics}")

    fine_tuner.close()
