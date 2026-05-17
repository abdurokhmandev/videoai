from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import os


class Settings(BaseSettings):
    # Bot
    BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bot.db"

    # fal.ai
    FAL_KEY: str = ""

    # Admin
    ADMIN_IDS: str = ""
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    MAINTENANCE_MODE: bool = False

    # Pricing (tangas)
    VIDEO_COST_TANGAS: int = 30
    WELCOME_BONUS_TANGAS: int = 50
    REFERRAL_BONUS_TANGAS: int = 20
    PREMIUM_COST_TANGAS: int = 500
    STREAK_7_BONUS: int = 10
    STREAK_3_BONUS: int = 2

    # Karta (qo'lda to'lov)
    CARD_NUMBER: str = "8600123456789012"
    CARD_OWNER: str = "Ism Familiya"

    # Stars Packages
    STARS_PACKAGE_SMALL: int = 150
    STARS_PACKAGE_MEDIUM: int = 420
    STARS_PACKAGE_LARGE: int = 1000
    STARS_PACKAGE_MEGA: int = 2100

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    @property
    def is_maintenance(self) -> bool:
        """Agarda BOT_TOKEN kiritilmagan bo'lsa yoki MAINTENANCE_MODE=True bo'lsa, texnik rejim yoqiladi"""
        return not bool(self.BOT_TOKEN.strip()) or self.MAINTENANCE_MODE

    @property
    def packages(self) -> Dict[str, Dict[str, Any]]:
        return {
            "small": {
                "name": "🥉 Kichik",
                "tangas": 60,
                "stars": self.STARS_PACKAGE_SMALL,
                "som": 18000,
            },
            "medium": {
                "name": "🥈 O'rta",
                "tangas": 180,
                "stars": self.STARS_PACKAGE_MEDIUM,
                "som": 50000,
            },
            "large": {
                "name": "🥇 Katta",
                "tangas": 450,
                "stars": self.STARS_PACKAGE_LARGE,
                "som": 120000,
            },
            "mega": {
                "name": "💎 Mega",
                "tangas": 1000,
                "stars": self.STARS_PACKAGE_MEGA,
                "som": 250000,
            },
        }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
