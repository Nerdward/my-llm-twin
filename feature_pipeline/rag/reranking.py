from typing import List

from feature_pipeline.llm.chain import GeneralChain
from feature_pipeline.llm.prompt_templates import RerankingTemplate


class Reranker:
    @staticmethod
    def generate_response(query: str, passages: List[str], keep_top_k: int) -> List[str]:
        reranking_template = RerankingTemplate()
        prompt_template = reranking_template.create_template(keep_top_k=keep_top_k)

        model = ChatOpenAI()
        chain = GeneralChain().get_chain(llm=model, output_key="rerank", template=prompt_template)

        stripped_passages = [stripped_item for item in passages if (stripped_item := item.strip())]
        passages = reranking_template.separator.join(stripped_passages)
        response = chain.invoke({"question": query, "passages": passages})

        result = response["rerank"]
        reranked_passages = result.strip().split(reranking_template.separator)
        stripped_passages = [
            stripped_item for item in reranked_passages if (stripped_item := item.strip())
        ]

        return stripped_passages
