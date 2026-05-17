from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import get_or_create_user, AsyncSessionLocal
from bot.utils.messages import get_msg
from bot.keyboards.main import settings_keyboard

router = Router()


@router.message(Command("settings"))
async def settings_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        # Sozlamalar matni
        text = get_msg(user.language, "settings").format(
            lang="🇺🇿 O'zbekcha" if user.language == "uz" else "🇷🇺 Русский"
        )
        await message.answer(text, reply_markup=settings_keyboard(user.language))


@router.callback_query(F.data == "settings")
async def settings_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "settings").format(
            lang="🇺🇿 O'zbekcha" if user.language == "uz" else "🇷🇺 Русский"
        )
        await callback.message.edit_text(text, reply_markup=settings_keyboard(user.language))
        await callback.answer()
