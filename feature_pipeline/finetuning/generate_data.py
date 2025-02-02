import json
from sys import exc_info

from comet_ml import Artifact, Experiment

from feature_pipeline.config import settings
from feature_pipeline.db import QdrantDatabaseConnector
from feature_pipeline.finetuning.file_handler import FileHandler
from feature_pipeline.finetuning.llm_communication import GptCommunicator
from feature_pipeline.utils.logging import get_logger

logger = get_logger(__name__)
client = QdrantDatabaseConnector()


class DataFormatter:
    @classmethod
    def get_system_prompt(cls, data_type: str) -> str:
        return (
            f"I will give you batches of contents of {data_type}. Please generate me exactly 1 instruction for each of them. The {data_type} text "
            f"for which you have to generate the instructions is under Content number x lines. Please structure the answer in json format,"
            f"ready to be loaded by json.loads(), a list of objects only with fields called instruction and content. For the content field, copy the number of the content only!."
            f"Please do not add any extra characters and make sure it is a list with objects in valid json format!\n"
        )

    @classmethod
    def format_data(cls, data_points: list, is_example: bool, start_index: int) -> str:
        text = ""
        for index, data_point in enumerate(data_points):
            if not is_example:
                text += f"Content number {start_index + index}\n"

            text += str(data_point) + "\n"

        return text

    @classmethod
    def format_batch(cls, context_msg: str, data_points: list, start_index: int) -> str:
        delimiter_msg = context_msg
        delimiter_msg += cls.format_data(data_points, False, start_index)

        return delimiter_msg

    @classmethod
    def format_prompt(cls, inference_posts: list, data_type: str, start_index: int) -> str:
        initial_prompt = cls.get_system_prompt(data_type)
        initial_prompt += f"You must generate exactly a list of {len(inference_posts)} json objects, using the contents provided under CONTENTS FOR GENERATION\n"
        initial_prompt += cls.format_batch(
            "\nCONTENTS FOR GENERATION: \n", inference_posts, start_index
        )

        return initial_prompt


class DatasetGenerator:
    def __init__(
        self,
        file_handler: FileHandler,
        api_communicator: GptCommunicator,
        data_formatter: DataFormatter,
    ) -> None:
        self.file_handler = file_handler
        self.api_communicator = api_communicator
        self.data_formatter = data_formatter

    def generate_training_data(self, collection_name: str, data_type: str, batch_size: int = 1):
        all_contents = self.fetch_all_cleaned_content(collection_name)
        response = []
        for i in range(0, len(all_contents), batch_size):
            batch = all_contents[i : i + batch_size]
            prompt = self.data_formatter.format_prompt(batch, data_type, i)
            response += self.api_communicator.send_prompt(prompt)
            for j in range(i, i + batch_size):
                response[j]["content"] = all_contents[j]

        self.push_to_comet(response, data_type, collection_name)

    def push_to_comet(self, data: list, data_type: str, collection_name: str):
        try:
            logger.info(f"Starting to push data to Comet: {collection_name}")

            experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE,
            )

            file_name = f"{collection_name}.json"
            logger.info(f"Writing data to file: {file_name}")

            with open(file_name, "w") as f:
                json.dump(data, f)

            logger.info("Data written to file successfully")
            artifact = Artifact(f"{data_type}-instruct-dataset")
            artifact.add(file_name)
            experiment.end()
            logger.info("Data pushed to Comet successfully and experiment ended")

        except Exception as e:
            logger.error(f"Failed to push data to Comet: {e}", exc_info=True)

    def fetch_all_cleaned_content(self, collection_name: str) -> list:
        all_cleaned_contents = []

        scroll_response = client.scroll(collection_name=collection_name, limit=10000)
        points = scroll_response[0]

        for point in points:
            cleaned_content = point.payload["cleaned_content"]
            if cleaned_content:
                all_cleaned_contents.append(cleaned_content)

        return all_cleaned_contents
