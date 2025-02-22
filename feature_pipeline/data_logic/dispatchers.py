from typing import List

from feature_pipeline.data_logic.chunking_data_handlers import (
    ArticleChunkingHandler,
    ChunkingDataHandler,
    PostChunkingHandler,
    RepositoryChunkingHandler,
)
from feature_pipeline.data_logic.cleaning_data_handlers import (
    ArticleCleaningHandler,
    CleaningDataHandler,
    PostCleaningHandler,
    RepositoryCleaningHandler,
)
from feature_pipeline.data_logic.embedding_data_handlers import (
    ArticleEmbeddingHandler,
    EmbeddingDataHandler,
    PostEmbeddingHandler,
    RepositoryEmbeddingHandler,
)
from feature_pipeline.models.base import DataModel
from feature_pipeline.models.raw import (
    ArticleRawModel,
    PostsRawModel,
    RepositoryRawModel,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


class RawDispatcher:
    @staticmethod
    def handle_mq_message(message: dict) -> DataModel:
        data_type = message.get("type")

        logger.info("Received message.", data_type=data_type)

        if data_type == "posts":
            return PostsRawModel(**message)
        elif data_type == "articles":
            return ArticleRawModel(**message)
        elif data_type == "repositories":
            return RepositoryRawModel(**message)
        else:
            raise ValueError("Unsupported data type")


class CleaningHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> CleaningDataHandler:
        if data_type == "posts":
            return PostCleaningHandler()
        elif data_type == "articles":
            return ArticleCleaningHandler()
        elif data_type == "repositories":
            return RepositoryCleaningHandler()
        else:
            raise ValueError("Unsupported data type")


class CleaningDispatcher:
    cleaning_factory = CleaningHandlerFactory()

    @classmethod
    def dispatch_cleaner(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        clean_model = handler.clean(data_model)

        logger.info(
            "Data cleaned successfully.",
            data_type=data_type,
            cleaned_content_len=len(clean_model.cleaned_content),
        )

        return clean_model


class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> ChunkingDataHandler:
        if data_type == "posts":
            return PostChunkingHandler()
        elif data_type == "articles":
            return ArticleChunkingHandler()
        elif data_type == "repositories":
            return RepositoryChunkingHandler()
        else:
            raise ValueError("Unsupported data type")


class ChunkingDispatcher:
    chunking_factory = ChunkingHandlerFactory()

    @classmethod
    def dispatch_chunker(cls, data_model: DataModel) -> List[DataModel]:
        data_type = data_model.type
        handler = cls.chunking_factory.create_handler(data_type)
        chunk_models = handler.chunk(data_model)

        logger.info(
            "Cleaned content chunked successfully.",
            num=len(chunk_models),
            data_type=data_type,
        )

        return chunk_models


class EmbeddingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> EmbeddingDataHandler:
        if data_type == "posts":
            return PostEmbeddingHandler()
        elif data_type == "articles":
            return ArticleEmbeddingHandler()
        elif data_type == "repositories":
            return RepositoryEmbeddingHandler()
        else:
            raise ValueError("Unsupported data type")


class EmbeddingDispatcher:
    embeddding_factory = EmbeddingHandlerFactory()

    @classmethod
    def dispatch_embedder(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.embeddding_factory.create_handler(data_type)
        embedded_chunk_model = handler.embedd(data_model)

        logger.ingo(
            "Chunk embedded successfully.",
            data_type=data_type,
            embedding_len=len(embedded_chunk_model.embedded_content),
        )

        return embedded_chunk_model
