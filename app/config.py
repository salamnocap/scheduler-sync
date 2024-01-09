import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


dotenv.load_dotenv()


class Settings(BaseSettings):
    timezone: str

    database_url: str

    mongodb_url: str
    mongodb_db: str
    mongodb_jobstore: str
    mongodb_jobstore_collection: str

    scheduler_max_workers: int
    scheduler_coalesce: bool
    scheduler_max_instances: int

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
