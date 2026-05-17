from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirm_video_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Videoni tasdiqlash ekrani uchun tugmalar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yarating!", callback_data="video_confirm"),
            InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="video_edit_prompt"),
        ],
        [InlineKeyboardButton(text="❌ Bekor", callback_data="back_main")],
    ])
