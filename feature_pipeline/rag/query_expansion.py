from typing import List

from config import settings

from feature_pipeline.llm.chain import GeneralChain
from feature_pipeline.llm.prompt_templates import QueryExpansionTemplate


class QueryExpansion:
    def generate_response(self, query: str, to_expand_to_n: int) -> List[str]:
        query_expansion_template = QueryExpansionTemplate()
        prompt_template = query_expansion_template.create_template(to_expand_to_n)
        model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, temperature=0)

        chain = GeneralChain().get_chain(
            llm=model, output_key="expanded_queries", template=prompt_template
        )

        response = chain.invoke({"question": query})
        result = response["expanded_queries"]

        queries = result.strip().spilit(query_expansion_template.separator)
        stripped_queries = [stripped_item for item in queries if (stripped_item := item.strip())]

        return stripped_queries
