from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_DATABASE_HOST: str = (
        "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"
    )
    MONGO_DATABASE_NAME: str = "twin"
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None

    # CometML config
    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT: str | None = None

    # Embeddings config
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 256
    EMBEDDING_SIZE: int = 384
    EMBEDDING_MODEL_DEVICE: str = "cpu"

    # OpenAI
    OPENAI_MODEL_ID: str = "gpt-4-1106-preview"
    OPENAI_API_KEY: str | None = None

    # MQ Config
    RABBITMQ_HOST: str  # or localhost if running outside Docker
    RABBITMQ_PORT: str
    RABBITMQ_DEFAULT_USERNAME: str
    RABBITMQ_DEFAULT_PASSWORD: str
    RABBITMQ_QUEUE_NAME: str = "default"

    # QdrantDB config
    QDRANT_DATABASE_HOST: str = "qdrant"  # or localhost if running outside Docker
    QDRANT_DATABASE_PORT: int = 6333
    USE_QDRANT_CLOUD: bool = False  # if True, fill in QDRANT_CLOUD_URL and QDRANT_APIKEY
    QDRANT_CLOUD_URL: str | None = None
    QDRANT_APIKEY: str | None = None


settings = Settings()
