import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from a .env file if available
load_dotenv()

class Config:
    """
    Configuration class for managing system-wide settings.
    """

    # === Database Settings ===
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # === LLM API Settings ===
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # === Ontology Domains ===
    ONTOLOGY_DOMAINS = ["legal", "healthcare", "education", "ai_ethics", "finance", "warfare", "general"]

    # === Export Directory ===
    EXPORT_DIR = os.getenv("EXPORT_DIR", "exports/")

    # === Logging Settings ===
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def log_config(cls):
        """
        Logs current system configuration (excluding sensitive credentials).
        """
        logger.info(f"Neo4j URI: {cls.NEO4J_URI}")
        logger.info(f"Redis Host: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
        logger.info(f"Ontology Domains: {cls.ONTOLOGY_DOMAINS}")
        logger.info(f"Export Directory: {cls.EXPORT_DIR}")
        logger.info(f"Log Level: {cls.LOG_LEVEL}")

if __name__ == "__main__":
    logger.info("Loading system configuration...")
    Config.log_config()
