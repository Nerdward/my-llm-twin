import hashlib
from abc import ABC, abstractmethod
from typing import List

from feature_pipeline.models.chunk import (
    ArticleChunkModel,
    PostChunkModel,
    RepositoryChunkModel,
)
from src.feature_pipeline.models.base import DataModel
from src.feature_pipeline.models.clean import (
    ArticleCleanedModel,
    PostCleanedModel,
    RepositoryCleanedModel,
)
from src.utils.chunking import chunk_text


class ChunkingDataHandler(ABC):
    """
    Abstract class for all Chunking data handlers.
    All data transformations logic for the chunking step is done here
    """

    @abstractmethod
    def chunk(self, data_model: DataModel) -> List[DataModel]:
        pass


class PostChunkingHandler(ChunkingDataHandler):
    def chunk(self, data_model: PostCleanedModel) -> List[PostChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = PostChunkModel(
                entry_id=data_model.entry_id,
                platform=data_model.platform,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                author_id=data_model.author_id,
                image=data_model.image if data_model.image else None,
                type=data_model.type,
            )

            data_models_list.append(model)

        return data_models_list


class ArticleChunkingHandler(ChunkingDataHandler):
    def chunk(self, data_model: ArticleCleanedModel) -> List[ArticleChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = ArticleChunkModel(
                entry_id=data_model.entry_id,
                platform=data_model.platform,
                link=data_model.link,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                author_id=data_model.author_id,
                type=data_model.type,
            )

            data_models_list.append(model)

        return data_models_list


class RepositoryChunkingHandler(ChunkingDataHandler):
    def chunk(self, data_model: RepositoryCleanedModel) -> List[RepositoryChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = RepositoryChunkModel(
                entry_id=data_model.entry_id,
                name=data_model.name,
                link=data_model.link,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                owner_id=data_model.owner_id,
                type=data_model.type,
            )

            data_models_list.append(model)

        return data_models_list
