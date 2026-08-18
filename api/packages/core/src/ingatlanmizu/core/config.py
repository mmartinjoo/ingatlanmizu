from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    environment: str = "local"
    log_level: str = "INFO"

    database_url: str = "postgresql://postgres:root@127.0.0.1:54320/ingatlanmizu"
    database_host: str = "127.0.0.1"
    database_port: int = "5432"
    database_user: str = "postgres"
    database_password: str = "root"
    database_db: str = "ingatlanmizu"
    migrations_dir: Path = Path("db/migrations")

    s3_endpoint_url: str
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    
    ingest_max_workers: int = 8

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
settings = Settings()