from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DOCX/TXT 脱敏验证 API"
    api_prefix: str = "/api/v1"
    max_upload_size_mb: int = 20
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MASKING_")

    @property
    def repo_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    @property
    def storage_dir(self) -> Path:
        return self.repo_root / "storage"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.storage_dir / 'app.db'}"

    @property
    def poc_core_dir(self) -> Path:
        return self.repo_root / "packages" / "poc-core"


settings = Settings()
