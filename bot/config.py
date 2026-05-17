from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Dict, Any
import os


class Settings(BaseSettings):
    # Bot
    BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bot.db"

    # SiliconFlow
    SILICONFLOW_API_KEY: str = ""

    # Atlas Cloud
    ATLASCLOUD_API_KEY: str = ""
    ATLASCLOUD_BASE_URL: str = "https://api.atlascloud.ai/v1"

    # Payme
    PAYME_MERCHANT_ID: str = ""
    PAYME_KEY: str = ""
    PAYME_TEST_KEY: str = ""
    PAYME_TEST_MODE: bool = True

    # Click
    CLICK_SERVICE_ID: str = ""
    CLICK_MERCHANT_ID: str = ""
    CLICK_SECRET_KEY: str = ""

    # Admin
    ADMIN_IDS: str = ""
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    MAINTENANCE_MODE: bool = False

    # Pricing (so'm)
    FAST_VIDEO_PRICE: int = 3000
    PREMIUM_VIDEO_PRICE: int = 5000
    FREE_VIDEO_VALUE_SOM: int = 3000
    REFERRAL_BONUS_SOM: int = 3000

    # Packages
    STARTER_PRICE: int = 15000
    STARTER_VIDEOS: int = 3
    STANDARD_PRICE: int = 40000
    STANDARD_VIDEOS: int = 12
    PRO_PRICE: int = 90000
    PRO_VIDEOS: int = 30
    ENTERPRISE_PRICE: int = 200000
    ENTERPRISE_VIDEOS: int = 75

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
    def payme_key_actual(self) -> str:
        if self.PAYME_TEST_MODE:
            return self.PAYME_TEST_KEY
        return self.PAYME_KEY

    @property
    def packages(self) -> Dict[str, Dict[str, Any]]:
        return {
            "starter": {
                "name": "🥉 Starter",
                "price": self.STARTER_PRICE,
                "videos": self.STARTER_VIDEOS,
                "price_per_video": self.STARTER_PRICE // self.STARTER_VIDEOS if self.STARTER_VIDEOS else 0,
            },
            "standard": {
                "name": "🥈 Standard",
                "price": self.STANDARD_PRICE,
                "videos": self.STANDARD_VIDEOS,
                "price_per_video": self.STANDARD_PRICE // self.STANDARD_VIDEOS if self.STANDARD_VIDEOS else 0,
            },
            "pro": {
                "name": "🥇 Pro",
                "price": self.PRO_PRICE,
                "videos": self.PRO_VIDEOS,
                "price_per_video": self.PRO_PRICE // self.PRO_VIDEOS if self.PRO_VIDEOS else 0,
            },
            "enterprise": {
                "name": "💎 Enterprise",
                "price": self.ENTERPRISE_PRICE,
                "videos": self.ENTERPRISE_VIDEOS,
                "price_per_video": self.ENTERPRISE_PRICE // self.ENTERPRISE_VIDEOS if self.ENTERPRISE_VIDEOS else 0,
            },
        }

    @property
    def is_maintenance(self) -> bool:
        """Agarda BOT_TOKEN kiritilmagan bo'lsa yoki MAINTENANCE_MODE=True bo'lsa, texnik rejim yoqiladi"""
        return not bool(self.BOT_TOKEN.strip()) or self.MAINTENANCE_MODE

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
