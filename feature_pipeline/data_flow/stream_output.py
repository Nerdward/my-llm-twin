from typing import List, Optional

from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Batch

from src.data_crawling.utils import get_logger
from src.feature_pipeline.db import QdrantDatabaseConnector
from src.feature_pipeline.models.base import VectorDBDataModel

logger = get_logger(__name__)


class QdrantOutput(DynamicSink):
    """
    Bytewax class that facilitates the connection to a Qdrant vector DB.
    Inherits DynamicSink because of the ability to create different sink sources
    (e.g, vector and non-vector collections)
    """

    def __init__(self, connection: QdrantDatabaseConnector, sink_type: str) -> None:
        self._connection = connection
        self._sink_type = sink_type

        try:
            self._connection.get_collection(collection_name="cleaned_posts")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="cleaned_posts",
            )

            self._connection.create_non_vector_collection(collection_name="cleaned_posts")

        try:
            self._connection.get_collection(collection_name="cleaned_articles")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="cleaned_articles",
            )
            self._connection.create_non_vector_collection(collection_name="cleaned_articles")

        try:
            self._connection.get_collection(collection_name="cleaned_repositories")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="cleaned_repositories",
            )

            self._connection.create_non_vector_collection(collection_name="cleaned_repositories")

        try:
            self._connection.get_collection(collection_name="vector_posts")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="vector_posts",
            )

            self._connection.create_vector_collection(collection_name="vector_posts")

        try:
            self._connection.get_collection(collection_name="vector_articles")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="vector_articles",
            )

            self._connection.create_vector_collection(collection_name="vector_articles")

        try:
            self._connection.get_collection(collection_name="vector_repositories")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="vector_repositories",
            )

            self._connection.create_vector_collection(collection_name="vector_repositories")

    def build(
        self, step_id: str, worker_index: int, worker_count: int
    ) -> Optional[StatelessSinkPartition]:
        if self._sink_type == "clean":
            QdrankCleanedDataSink(connection=self._connection)
        elif self._sink_type == "vector":
            QdrankVectorDataSink(connection=self._connection)
        else:
            raise ValueError(f"Unsupported sink type: {self._sink_type}")


class QdrankCleanedDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector) -> None:
        self._client = connection

    def write_batch(self, items: List[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, data = zip(*payloads)
        collection_name = get_clean_collection(data_type=data[0]["type"])
        self._client.write_data(
            collection_name=collection_name, points=Batch(ids=ids, vectors={}, payloads=data)
        )

        logger.info(
            "Successfully inserted requested cleaned point(s)",
            collection_name=collection_name,
            num=len(ids),
        )


class QdrankVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector) -> None:
        self._client = connection

    def write_batch(self, items: List[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, vectors, metadata = zip(*payloads)
        collection_name = get_vector_collection(data_type=metadata[0]["type"])
        self._client.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors=vectors, payloads=metadata),
        )

        logger.info(
            "Successfully inserted requested cleaned point(s)",
            collection_name=collection_name,
            num=len(ids),
        )


def get_clean_collection(data_type: str) -> str:
    if data_type == "posts":
        return "cleaned_posts"
    elif data_type == "articles":
        return "cleaned_articles"
    elif data_type == "repositories":
        return "cleaned_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")


def get_vector_collection(data_type: str) -> str:
    if data_type == "posts":
        return "vector_posts"
    elif data_type == "articles":
        return "vector_articles"
    elif data_type == "repositories":
        return "vector_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
