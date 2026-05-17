from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os

class Settings(BaseSettings):
    # Bot
    BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bot.db"

    # ... (other settings unchanged) ...
    ADMIN_IDS: str = ""
    # Pricing etc.

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    @property
    def maintenance(self) -> bool:
        """Return True when required config (BOT_TOKEN) is missing."""
        return not bool(self.BOT_TOKEN)

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
