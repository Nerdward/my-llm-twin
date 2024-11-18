from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_DATABASE_HOST: str = (
        "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"
    )
    MONGO_DATABASE_NAME: str = "twin"
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None
    RABBITMQ_HOST: str  # or localhost if running outside Docker
    RABBITMQ_PORT: str
    RABBITMQ_DEFAULT_USERNAME: str
    RABBITMQ_DEFAULT_PASSWORD: str
    RABBITMQ_QUEUE_NAME: str = "default"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
