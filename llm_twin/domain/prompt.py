from llm_twin.domain.base import VectorBaseDocument
from llm_twin.domain.cleaned_documents import CleanedDocument
from llm_twin.domain.types import DataCategory


class Prompt(VectorBaseDocument):
    template: str
    input_variables: dict
    content: str
    num_tokens: int | None = None

    class Config:
        category = DataCategory.PROMPT


class GenerateDatasetSamplesPrompt(Prompt):
    data_category: DataCategory
    document: CleanedDocument
