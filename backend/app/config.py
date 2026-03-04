from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "MediaStack"
    debug: bool = False

    # Logging
    enable_access_log: bool = False  # Set to true to enable all request logging

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/db/mediastack.db"

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Storage
    storage_path: Path = Path("./data/videos")

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env"}


settings = Settings()
