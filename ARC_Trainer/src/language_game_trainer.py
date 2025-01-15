from neo4j import GraphDatabase
from loguru import logger
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class LanguageGameTrainer:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Language Game Trainer with Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("LanguageGameTrainer initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def fetch_training_data(self, game_name):
        """
        Fetch training data for a specific language game from Neo4j.

        Args:
            game_name (str): Name of the language game.

        Returns:
            list: Training data consisting of input/output pairs.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (g:Game {name: $game_name})-[:HAS_TRAINING_DATA]->(d:Data)
                    RETURN d.input AS input, d.output AS output
                    """,
                    game_name=game_name
                )
                training_data = [
                    {"input": record["input"], "output": record["output"]}
                    for record in result
                ]
                logger.info(f"Fetched {len(training_data)} training examples for game {game_name}.")
                return training_data
        except Exception as e:
            logger.error(f"Error fetching training data for {game_name}: {e}")
            return []

    def train_model(self, game_name, model, test_size=0.2):
        """
        Train a model for the specified language game using stored training data.

        Args:
            game_name (str): Name of the language game.
            model: Machine learning model to train.
            test_size (float): Proportion of the data to use for testing.

        Returns:
            dict: Training results including accuracy and any errors encountered.
        """
        try:
            data = self.fetch_training_data(game_name)

            if not data:
                logger.warning(f"No training data found for game {game_name}.")
                return {"status": "failed", "error": "No data"}

            inputs = [d["input"] for d in data]
            outputs = [d["output"] for d in data]

            X_train, X_test, y_train, y_test = train_test_split(
                inputs, outputs, test_size=test_size, random_state=42
            )

            logger.info("Starting model training...")
            model.fit(X_train, y_train)

            logger.info("Evaluating model...")
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)

            logger.info(f"Training completed with accuracy: {accuracy:.2f}")
            return {"status": "success", "accuracy": accuracy}

        except Exception as e:
            logger.error(f"Error training model for game {game_name}: {e}")
            return {"status": "failed", "error": str(e)}

    def save_model(self, game_name, model):
        """
        Save a trained model to Neo4j for future use.

        Args:
            game_name (str): Name of the language game.
            model: Trained machine learning model.
        """
        try:
            serialized_model = model.get_params()
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (g:Game {name: $game_name})
                    SET g.model = $model
                    """,
                    game_name=game_name,
                    model=serialized_model
                )
                logger.info(f"Model for game {game_name} saved successfully.")
        except Exception as e:
            logger.error(f"Error saving model for game {game_name}: {e}")

if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier

    logger.info("Initializing Language Game Trainer")
    trainer = LanguageGameTrainer(uri="bolt://localhost:7687", user="neo4j", password="password")

    # Example: Training a RandomForest model for a game
    game_name = "example_game"
    model = RandomForestClassifier()

    results = trainer.train_model(game_name, model)
    if results["status"] == "success":
        logger.info(f"Training succeeded with accuracy: {results['accuracy']:.2f}")
        trainer.save_model(game_name, model)
    else:
        logger.error("Training failed.")

    trainer.close()
