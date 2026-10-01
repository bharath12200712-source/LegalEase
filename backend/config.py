from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "LegalEase"
    company_name: str = "LegalEase"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    backend_url: str = "http://127.0.0.1:8000"

    logo_path: str = "assets/logo.png"

    max_input_chars: int = 20_000
    max_output_chars: int = 50_000

    request_timeout_seconds: int = 90

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def resolved_logo_path(self) -> Path:
        path = Path(self.logo_path)

        if path.is_absolute():
            return path

        return BASE_DIR / path


@lru_cache
def get_settings() -> Settings:
    return Settings()