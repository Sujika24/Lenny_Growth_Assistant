import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Database
    database_url: Optional[str] = "postgresql+psycopg://postgres:postgres@localhost:5432/lenny_growth"
    sqlite_fallback_url: str = "sqlite:///./lenny_growth.db"

    # Transcripts & Vector Store
    transcripts_data_dir: str = "data/lenny_repo/episodes"
    chroma_persist_dir: str = "data/chroma_db"
    retrieval_top_k: int = 4
    retrieval_similarity_threshold: float = 0.30

    # Local Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: int = 90

    # Cloud Providers
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    default_provider: str = "ollama"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
