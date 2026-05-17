from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def packages_keyboard() -> InlineKeyboardMarkup:
    """Tanga olish uchun paketlar ro'yxati"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 60 tanga — 150 ⭐ yoki 18,000 so'm",
            callback_data="pkg_small"
        )],
        [InlineKeyboardButton(
            text="🥈 180 tanga — 420 ⭐ yoki 50,000 so'm ⭐ MASHHUR",
            callback_data="pkg_medium"
        )],
        [InlineKeyboardButton(
            text="🥇 450 tanga — 1000 ⭐ yoki 120,000 so'm",
            callback_data="pkg_large"
        )],
        [InlineKeyboardButton(
            text="💎 1000 tanga — 2100 ⭐ yoki 250,000 so'm",
            callback_data="pkg_mega"
        )],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])


def payment_methods_keyboard(package_key: str) -> InlineKeyboardMarkup:
    """Paket tanlangandan keyin to'lov usullari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⭐ Telegram Stars",
            callback_data=f"pay_stars_{package_key}"
        )],
        [InlineKeyboardButton(
            text="💳 Karta orqali (qo'lda)",
            callback_data=f"pay_manual_{package_key}"
        )],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="topup")]
    ])


def manual_payment_confirm_keyboard(package_key: str) -> InlineKeyboardMarkup:
    """Qo'lda karta orqali to'lov chekini yuborishni tasdiqlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Chekni yubordim",
            callback_data=f"confirm_receipt_{package_key}"
        )],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="topup")]
    ])


def balance_low_keyboard() -> InlineKeyboardMarkup:
    """Balans yetmaganida topup-ga yoki do'stlarga yo'naltiruvchi klaviatura"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ Stars bilan olish", callback_data="topup"),
            InlineKeyboardButton(text="💳 Karta orqali olish", callback_data="topup"),
        ],
        [InlineKeyboardButton(text="👥 Do'st taklif qil (+20 🪙)", callback_data="referral")]
    ])


def admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel boshqaruv tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="👥 Userlar", callback_data="admin_users"),
            InlineKeyboardButton(text="💰 Tranzaksiyalar", callback_data="admin_payments")
        ],
        [
            InlineKeyboardButton(text="🎬 So'nggi videolar", callback_data="admin_videos"),
            InlineKeyboardButton(text="🏆 Top userlar", callback_data="admin_top")
        ],
        [
            InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="back_main")
        ]
    ])

