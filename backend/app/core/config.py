"""Application settings, loaded from environment variables / the project-root .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "development"
    database_url: str = "sqlite:///./healthcare.db"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    # Comma-separated list. Kept as a string so it can be written plainly in .env.
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )
    appointment_duration_minutes: int = 30
    secret_key: str = Field(default="development-only-change-this-secret-key", min_length=32)
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    @field_validator("appointment_duration_minutes")
    @classmethod
    def _duration_divides_hour(cls, value: int) -> int:
        if value < 5 or 60 % value != 0:
            raise ValueError("APPOINTMENT_DURATION_MINUTES must divide 60 evenly (e.g. 10, 15, 20, 30, 60)")
        return value

    @model_validator(mode="after")
    def _no_wildcard_cors_in_production(self) -> "Settings":
        if self.app_env.lower() == "production" and "*" in self.cors_origin_list:
            raise ValueError("CORS_ORIGINS must not contain '*' when APP_ENV=production")
        if self.app_env.lower() == "production" and self.secret_key in {
            "development-only-change-this-secret-key",
            "replace-this-with-a-long-random-secret-key",
        }:
            raise ValueError("SECRET_KEY must be set to a strong random value in production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_database_url(self) -> str:
        """Make relative SQLite paths relative to backend/, regardless of the working directory."""
        prefix = "sqlite:///"
        url = self.database_url
        if url.startswith(prefix) and not url.startswith("sqlite:////") and ":memory:" not in url:
            raw = url[len(prefix):]
            if not Path(raw).is_absolute():
                return f"{prefix}{(BACKEND_DIR / raw).resolve().as_posix()}"
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
