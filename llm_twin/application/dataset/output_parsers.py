from typing import Any
from langchain.output_parsers import PydanticOutputParser


class ListPydanticOutputParser(PydanticOutputParser):
    def _parse_obj(self, obj: dict | list) -> Any:
        if isinstance(obj, list):
            return [
                super(ListPydanticOutputParser, self)._parse_obj(obj_) for obj_ in obj
            ]
        else:
            return super(ListPydanticOutputParser, self)._parse_obj(obj)
