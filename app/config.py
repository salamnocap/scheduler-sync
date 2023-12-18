import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


dotenv.load_dotenv()


class Settings(BaseSettings):
    database_url: str
    mongodb_url: str
    mongodb_db: str
    broker_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
