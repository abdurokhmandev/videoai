from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy pastki menyu (Reply keyboard)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Video yaratish")],
            [KeyboardButton(text="🪙 Balans"), KeyboardButton(text="📋 Tarix")],
            [KeyboardButton(text="👥 Do'stlar"), KeyboardButton(text="🏆 Reyting")]
        ],
        resize_keyboard=True
    )


def main_inline_keyboard() -> InlineKeyboardMarkup:
    """Asosiy inline navigatsiya menyusi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Video yaratish", callback_data="video_start")],
        [
            InlineKeyboardButton(text="🪙 Tanga olish", callback_data="topup"),
            InlineKeyboardButton(text="📋 Tarix", callback_data="history_0")
        ],
        [
            InlineKeyboardButton(text="👥 Do'stlar", callback_data="referral"),
            InlineKeyboardButton(text="🏆 Reyting", callback_data="top_users")
        ]
    ])


def back_button(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")],
    ])


def language_select_keyboard() -> InlineKeyboardMarkup:
    """Faqat yangi foydalanuvchilar til tanlashi uchun (ortiqcha orqaga tugmasisiz)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
        ],
    ])


def settings_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")],
    ])


def after_video_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Video yaratilgandan keyin ko'rsatiladigan tugmalar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Yana video", callback_data="video_start"),
            InlineKeyboardButton(text="🪙 Tanga olish", callback_data="topup"),
        ],
        [InlineKeyboardButton(text="📤 Do'stga yubor", switch_inline_query="Zo'r bot, matn kiritib AI video yarating!")]
    ])


def balance_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Balans sahifasidagi tugmalar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🪙 Tanga olish", callback_data="topup"),
            InlineKeyboardButton(text="📋 Tarix", callback_data="history_0"),
        ],
    ])


def referral_keyboard(ref_link: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Referral sahifasidagi tugmalar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Ulashish", switch_inline_query=f"AI orqali video yarating! 50 bepul tanga olish uchun havola: {ref_link}")],
        [InlineKeyboardButton(text="📊 Batafsil", callback_data="ref_details")],
    ])
