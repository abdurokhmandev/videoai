"""To'lov klaviaturalari"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import settings


def packages_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    pkgs = settings.packages
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"🥉 Starter — {pkgs['starter']['price']:,} сум ({pkgs['starter']['videos']} видео)",
                callback_data="pkg_starter"
            )],
            [InlineKeyboardButton(
                text=f"🥈 Standard — {pkgs['standard']['price']:,} сум ({pkgs['standard']['videos']} видео) ⭐",
                callback_data="pkg_standard"
            )],
            [InlineKeyboardButton(
                text=f"🥇 Pro — {pkgs['pro']['price']:,} сум ({pkgs['pro']['videos']} видео)",
                callback_data="pkg_pro"
            )],
            [InlineKeyboardButton(
                text=f"💎 Enterprise — {pkgs['enterprise']['price']:,} сум ({pkgs['enterprise']['videos']} видео)",
                callback_data="pkg_enterprise"
            )],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🥉 Starter — {pkgs['starter']['price']:,} so'm ({pkgs['starter']['videos']} video)",
            callback_data="pkg_starter"
        )],
        [InlineKeyboardButton(
            text=f"🥈 Standard — {pkgs['standard']['price']:,} so'm ({pkgs['standard']['videos']} video) ⭐ MASHHUR",
            callback_data="pkg_standard"
        )],
        [InlineKeyboardButton(
            text=f"🥇 Pro — {pkgs['pro']['price']:,} so'm ({pkgs['pro']['videos']} video)",
            callback_data="pkg_pro"
        )],
        [InlineKeyboardButton(
            text=f"💎 Enterprise — {pkgs['enterprise']['price']:,} so'm ({pkgs['enterprise']['videos']} video)",
            callback_data="pkg_enterprise"
        )],
    ])


def payment_method_keyboard(package_key: str, lang: str = "uz") -> InlineKeyboardMarkup:
    back_text = "◀️ Orqaga" if lang == "uz" else "◀️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Payme", callback_data=f"pay_payme_{package_key}"),
            InlineKeyboardButton(text="🔵 Click", callback_data=f"pay_click_{package_key}"),
        ],
        [InlineKeyboardButton(text=back_text, callback_data="topup")],
    ])


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 To'liq statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Userlar", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="💰 Tranzaksiyalar", callback_data="admin_payments"),
        ],
        [
            InlineKeyboardButton(text="🎬 Videolar", callback_data="admin_videos"),
            InlineKeyboardButton(text="🏆 Top userlar", callback_data="admin_top"),
        ],
    ])
