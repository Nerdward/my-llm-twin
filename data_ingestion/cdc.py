import json
import logging

from bson import json_util

from data_ingestion.config import settings
from data_ingestion.db import MongoDatabaseConnector
from data_ingestion.mq import publish_to_rabbitmq

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def stream_process():
    try:
        client = MongoDatabaseConnector()
        db = client["twin"]
        logging.info("Connected to MongoDB.")

        changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])

        for change in changes:
            data_type = change["ns"]["coll"]
            entry_id = str(change["fullDocument"]["_id"])

            change["fullDocument"].pop("_id")
            change["fullDocument"]["type"] = data_type
            change["fullDocument"]["entry_id"] = entry_id

            if data_type not in ["articles", "posts", "repositories"]:
                logging.info(f"Unsupported data type: '{data_type}'")
                continue

            data = json.dumps(change["fullDocument"], default=json_util.default)
            logging.info(f"Change detected and serialized for a data sample of type {data_type}.")

            publish_to_rabbitmq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=data)
            logging.info(f"Data of type '{data_type}' published to RabbitMQ.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    stream_process()
