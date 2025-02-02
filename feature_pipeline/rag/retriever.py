import concurrent.futures
from typing import List

from config import settings
from qdrant_client import models
from sentence_transformers.SentenceTransformer import SentenceTransformer

from feature_pipeline import utils
from feature_pipeline.db import QdrantDatabaseConnector
from feature_pipeline.rag.query_expansion import QueryExpansion
from feature_pipeline.rag.reranking import Reranker
from feature_pipeline.rag.self_query import SelfQuery
from feature_pipeline.utils.logging import get_logger

logger = get_logger(__name__)


class VectorRetriever:
    """
    A class for retrieving from a Vector Store in a RAG system
    using query expansion and Multitenancy search.
    """

    def __init__(self, query: str) -> None:
        self._client = QdrantDatabaseConnector()
        self.query = query
        self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(self, generated_query: str, metadata_filter_value: str | None, k: int):
        assert k > 3, "K should be greater than 3"

        query_vector = self._embedder.encode(generated_query).tolist()
        vectors = [
            self._client.search(
                collection_name="vector_posts",
                query_filter=(
                    models.Filter(
                        must=[
                            models.FieldCondition(
                                key="author_id",
                                match=models.MatchValue(value=metadata_filter_value),
                            )
                        ]
                    )
                    if metadata_filter_value
                    else None
                ),
                query_vector=query_vector,
                limit=k // 3,
            ),
            self._client.search(
                collection_name="vector_articles",
                query_filter=(
                    models.Filter(
                        must=[
                            models.FieldCondition(
                                key="author_id",
                                match=models.MatchValue(value=metadata_filter_value),
                            )
                        ]
                    )
                    if metadata_filter_value
                    else None
                ),
                query_vector=query_vector,
                limit=k // 3,
            ),
            self._client.search(
                collection_name="vector_repositories",
                query_filter=(
                    models.Filter(
                        must=[
                            models.FieldCondition(
                                key="author_id",
                                match=models.MatchValue(value=metadata_filter_value),
                            )
                        ]
                    )
                    if metadata_filter_value
                    else None
                ),
                query_vector=query_vector,
                limit=k // 3,
            ),
        ]

        return utils.flatten(vectors)

    def retrieve_top_k(self, k: int, to_expand_to_n_queries: int) -> List:
        generated_queries = self._query_expander.generate_response(
            self.query, to_expand_to_n=to_expand_to_n_queries
        )

        logger.info(
            "Successfully generated queries for search.",
            num_queries=len(generated_queries),
        )

        author_id = self._metadata_extractor.generate_response(self.query)
        if author_id:
            logger.info(
                "Successfully extracted the author_id from thw query.",
                author_id=author_id,
            )
        else:
            logger.info("Couldn't extract the author_id from the query.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, author_id, k)
                for query in generated_queries
            ]

            hits = [task.result() for task in concurrent.futures.as_completed(search_tasks)]

            hits = utils.flatten(hits)

        logger.info("All documents retrireved successfully.", num_documents=len(hits))

        return hits

    def rerank(self, hits: list, keep_top_k: int) -> List[str]:
        content_list = [hit.payload["content"] for hit in hits]
        rerank_hits = self._reranker.generate_response(
            query=self.query, passages=content_list, keep_top_k=keep_top_k
        )

        logger.info("Documents reranked successfully.", num_documents=len(rerank_hits))

        return rerank_hits

    def set_query(self, query: str) -> None:
        self.query = query
