from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env")

    database_url: str = f"sqlite:///{BACKEND_DIR / 'data' / 'leads.db'}"

settings = Settings()
