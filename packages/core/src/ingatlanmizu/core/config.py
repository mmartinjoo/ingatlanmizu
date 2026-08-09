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

    database_url: str = "postgresql://postgres:root@127.0.01:54320/ingatlanmizu"
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
    
settings = Settings()