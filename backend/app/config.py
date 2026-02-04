from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tasks"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    task_queue_name: str = "task_queue"
    app_host: str = "0.0.0.0"
    app_port: int = 8000


settings = Settings()
