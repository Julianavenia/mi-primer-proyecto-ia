from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    llm_backend: Literal["fake", "anthropic"] = "fake"
    anthropic_api_key: str | None = None
    model_name: str = "claude-sonnet-5"
    max_tool_iterations: int = 10
    max_tokens: int = 1024
    # Orígenes explícitos permitidos por CORS. Ya es un campo de Settings, así que
    # se puede sobreescribir por variable de entorno (CORS_ALLOWED_ORIGINS, como
    # JSON: '["http://localhost:3000","https://mi-dominio.com"]') sin tocar código
    # cuando el frontend se despliegue en otro origen. Nunca usar "*".
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ]
