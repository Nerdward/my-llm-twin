from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from llm_twin.settings import settings


class MongoDatabaseConnector:
    """Singleton class to connect to MongoDB database."""

    _instance: MongoClient | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.DATABASE_HOST)
            except ConnectionFailure as e:
                logger.error(f"Could not connect to the database: {str(e)}")
                raise

        print(f"Connection to database with uri: {settings.DATABASE_HOST}")

        return cls._instance


connection = MongoDatabaseConnector()
