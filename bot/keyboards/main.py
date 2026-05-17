"""Asosiy inline klaviaturalar"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Создать видео", callback_data="video_start"),
                InlineKeyboardButton(text="💰 Пополнить", callback_data="topup"),
            ],
            [
                InlineKeyboardButton(text="📋 Пакеты", callback_data="topup"),
                InlineKeyboardButton(text="🔗 Пригласить", callback_data="referral"),
            ],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Video yasash", callback_data="video_start"),
            InlineKeyboardButton(text="💰 Balans to'ldirish", callback_data="topup"),
        ],
        [
            InlineKeyboardButton(text="📋 Paketlar", callback_data="topup"),
            InlineKeyboardButton(text="🔗 Do'st taklif qil", callback_data="referral"),
        ],
    ])


def back_button(lang: str = "uz") -> InlineKeyboardMarkup:
    text = "◀️ Orqaga" if lang == "uz" else "◀️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="back_main")],
    ])


def settings_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
        ],
        [InlineKeyboardButton(
            text="◀️ Orqaga" if lang == "uz" else "◀️ Назад",
            callback_data="back_main"
        )],
    ])


def after_video_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Ещё видео", callback_data="video_start"),
                InlineKeyboardButton(text="💰 Пополнить", callback_data="topup"),
            ],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Yana bir video", callback_data="video_start"),
            InlineKeyboardButton(text="💰 Balans to'ldirish", callback_data="topup"),
        ],
    ])


def balance_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Пополнить", callback_data="topup"),
                InlineKeyboardButton(text="📋 История", callback_data="history_0"),
            ],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Balans to'ldirish", callback_data="topup"),
            InlineKeyboardButton(text="📋 Video tarixi", callback_data="history_0"),
        ],
    ])


def history_keyboard(offset: int, total: int, lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    nav = []
    if offset > 0:
        prev_text = "◀️ Oldingi" if lang == "uz" else "◀️ Назад"
        nav.append(InlineKeyboardButton(text=prev_text, callback_data=f"history_{offset - 10}"))
    if offset + 10 < total:
        next_text = "Keyingi ▶️" if lang == "uz" else "Далее ▶️"
        nav.append(InlineKeyboardButton(text=next_text, callback_data=f"history_{offset + 10}"))
    if nav:
        buttons.append(nav)
    new_text = "🎬 Yangi video" if lang == "uz" else "🎬 Новое видео"
    buttons.append([InlineKeyboardButton(text=new_text, callback_data="video_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def referral_keyboard(ref_link: str, lang: str = "uz") -> InlineKeyboardMarkup:
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=f"Создавайте AI видео! {ref_link}")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Ulashish", switch_inline_query=f"AI video yarating! {ref_link}")],
    ])
