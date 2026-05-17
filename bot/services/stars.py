from aiogram.types import LabeledPrice
from typing import Dict, Any

def get_stars_invoice(package_key: str, package_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Telegram Stars orqali invoice yuborish uchun kerakli parametrlarni qaytaradi.
    valyuta Stars uchun hamisha 'XTR' va provider_token bo'sh ('') bo'lishi kerak.
    """
    title = f"{package_data['name']} paket — {package_data['tangas']} tanga"
    description = f"AI Videochi botida video yaratish uchun {package_data['tangas']} tanga sotib olish."
    payload = f"stars_pkg_{package_key}"
    
    prices = [
        LabeledPrice(label="⭐ Stars", amount=package_data["stars"])
    ]
    
    return {
        "title": title,
        "description": description,
        "payload": payload,
        "provider_token": "",  # Stars uchun bo'sh
        "currency": "XTR",     # Telegram Stars
        "prices": prices,
    }
