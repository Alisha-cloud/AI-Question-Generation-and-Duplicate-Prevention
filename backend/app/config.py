from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Induseuro Question Intelligence API"
    api_prefix: str = "/api/v1"
    data_file: str = "./data/questions.json"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    duplicate_threshold: float = 0.82
    review_threshold: float = 0.68
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
