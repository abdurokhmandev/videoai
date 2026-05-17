from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def model_select_keyboard() -> InlineKeyboardMarkup:
    """AI Modelini tanlash tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ Tezkor AI (15 🪙)", callback_data="select_model_fast"),
            InlineKeyboardButton(text="💎 Premium AI (30 🪙)", callback_data="select_model_best")
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])

def mode_select_keyboard() -> InlineKeyboardMarkup:
    """Video yaratish rejimini tanlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Shunchaki Prompt", callback_data="select_mode_text"),
            InlineKeyboardButton(text="🖼️ Rasm + Prompt", callback_data="select_mode_image")
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="video_start")]
    ])

def video_details_keyboard() -> InlineKeyboardMarkup:
    """Tavsif va namunaviy video ko'rilgandan keyin tasdiqlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Yaratishni boshlash", callback_data="details_confirm")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="video_select_mode")]
    ])

def confirm_video_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Yakuniy tasdiqlash ekrani"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Video yaratish!", callback_data="video_confirm"),
            InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="video_edit_prompt"),
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_main")],
    ])
