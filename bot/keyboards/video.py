"""Video oqimi klaviaturalari"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def model_select_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Быстрое", callback_data="model_fast"),
                InlineKeyboardButton(text="🏆 Премиум", callback_data="model_premium"),
            ],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ Tez va arzon", callback_data="model_fast"),
            InlineKeyboardButton(text="🏆 Premium", callback_data="model_premium"),
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")],
    ])


def confirm_video_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, создать!", callback_data="video_confirm"),
                InlineKeyboardButton(text="✏️ Изменить", callback_data="video_edit_prompt"),
            ],
            [InlineKeyboardButton(text="◀️ Отмена", callback_data="back_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, yarating!", callback_data="video_confirm"),
            InlineKeyboardButton(text="✏️ Promptni o'zgart.", callback_data="video_edit_prompt"),
        ],
        [InlineKeyboardButton(text="◀️ Bekor qilish", callback_data="back_main")],
    ])
