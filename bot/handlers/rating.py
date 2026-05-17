from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import get_top_users, get_or_create_user, AsyncSessionLocal
from bot.keyboards.main import back_button
from bot.utils.helpers import truncate_text

router = Router()


@router.message(F.text == "🏆 Reyting")
@router.message(Command("rating"))
async def rating_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, message.from_user.id, None, None)
        
        top_list = await get_top_users(session, limit=10)
        
        text = "🏆 <b>ENG FAOL FOYDALANUVCHILAR REYTINGI</b>\n\n"
        text += "Jami tangalar sarflash bo'yicha eng yuqori 10 ta yetakchimiz:\n\n"
        
        if not top_list:
            text += "<i>Hozircha reyting bo'sh. Birinchi videongizni yarating va yetakchiga aylaning!</i>"
        else:
            for idx, u in enumerate(top_list, start=1):
                name = u.full_name or u.username or f"User_{u.id}"
                name_clean = truncate_text(name, max_len=18)
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                medal = medals.get(idx, f"{idx}.")
                text += f"{medal} <b>{name_clean}</b> — 🎬 {u.total_videos} ta video ({u.total_spent} 🪙)\n"
                
        text += "\n━━━━━━━━━━━━━━━━━━━━\n"
        text += "🚀 Do'stlarni taklif qiling, ko'proq videolar yarating va reyting cho'qqisini zabt eting!"
        
        await message.answer(text, reply_markup=back_button(user.language))


@router.callback_query(F.data == "top_users")
async def rating_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        top_list = await get_top_users(session, limit=10)
        
        text = "🏆 <b>ENG FAOL FOYDALANUVCHILAR REYTINGI</b>\n\n"
        text += "Jami tangalar sarflash bo'yicha eng yuqori 10 ta yetakchimiz:\n\n"
        
        if not top_list:
            text += "<i>Hozircha reyting bo'sh. Birinchi videongizni yarating va yetakchiga aylaning!</i>"
        else:
            for idx, u in enumerate(top_list, start=1):
                name = u.full_name or u.username or f"User_{u.id}"
                name_clean = truncate_text(name, max_len=18)
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                medal = medals.get(idx, f"{idx}.")
                text += f"{medal} <b>{name_clean}</b> — 🎬 {u.total_videos} ta video ({u.total_spent} 🪙)\n"
                
        text += "\n━━━━━━━━━━━━━━━━━━━━\n"
        text += "🚀 Do'stlarni taklif qiling, ko'proq videolar yarating va reyting cho'qqisini zabt eting!"
        
        await callback.message.edit_text(text, reply_markup=back_button(user.language))
        await callback.answer()
