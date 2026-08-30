from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env")

    database_url: str
    staff_allowlist: str = ""
    frontend_domain: str
    log_magic_links: bool = True
    secure_cookies: bool = False
    resend_api_key: str
    resend_sender_email: str
    generate_demo_data: bool = False # so that tests can run without generating demo data

    @property 
    def staff_emails(self) -> set[str]:
    # property that splits, trims, and lowercases staff_allowlist    
        return {
            email.strip().lower() # drop accidental whitespace (e.g " email") and convert to lowercase
            for email in self.staff_allowlist.split(",") # split on comma
            if email.strip() # drop accidental whitespace or extra commas (e.g email,,email,)
        }


settings = Settings()
