from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    reddit_client_id: str
    reddit_client_secret: str
    reddit_redirect_uri: str
    secret_key: str
    database_url: str = "sqlite+aiosqlite:///data/reddit_hive.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
