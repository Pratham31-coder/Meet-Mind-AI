from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    mistral_api_key: str = ""
    sarvam_api_key: str = ""
    whisper_model: str = "small"
    sarvam_stt_model: str = "saaras:v3"
    gemini_model: str = "gemini-3.8-flash"
    cors_origins: str = "http://localhost:5173"
    database_url: str = f"sqlite:///{(ROOT_DIR / 'backend' / 'data' / 'meetings.db').as_posix()}"
    max_upload_bytes: int = 200 * 1024 * 1024
    data_dir: Path = ROOT_DIR / "backend" / "data"


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
(settings.data_dir / "uploads").mkdir(exist_ok=True)
(settings.data_dir / "jobs").mkdir(exist_ok=True)
