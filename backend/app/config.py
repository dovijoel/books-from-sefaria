from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database – SQLite for local dev; override via DATABASE_URL env var for Postgres
    database_url: str = "sqlite:///./sefaria.db"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # App
    secret_key: str = "dev-secret-key-change-in-production"
    environment: str = "development"
    log_level: str = "INFO"

    # Paths – override via .env for local dev
    pdf_output_dir: str = "/tmp/pdf_output"
    sefaria_links_dir: str = "./links"
    links_dir: str = "/app/links"
    resources_dir: str = "/app/resources"

    # HTTP timeout for Sefaria calls
    http_timeout: float = 30.0


settings = Settings()
