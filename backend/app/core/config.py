from functools import cached_property
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "MODERN_AI_PLATFORM"
    environment: str = "development"
    backend_cors_origins: list[str] = ["http://localhost:3000"]    
    database_url: str
    jwt_secret_key: str = Field(default="change-me", min_length=8)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    gemini_api_key: str =  os.getenv("GEMINI_API_KEY")
    jsearch_api_key: str = os.getenv("JSEARCH_API_KEY")
    jsearch_api_host: str = "jsearch.p.rapidapi.com"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    upload_dir: str = "uploads"
    max_upload_mb: int = 8

    @cached_property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins if origin.strip()]


settings = Settings()
