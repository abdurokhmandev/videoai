from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import get_or_create_user, AsyncSessionLocal
from bot.utils.messages import get_msg
from bot.keyboards.main import referral_keyboard, back_button
from bot.config import settings

router = Router()


async def get_referral_response(user, bot_username: str):
    # Referral ma'lumotlarini tayyorlash
    bonus_val = settings.REFERRAL_BONUS_SOM
    saved_val = user.total_referred * bonus_val
    
    text = get_msg(user.language, "referral_info").format(
        bot_username=bot_username,
        ref_code=user.referral_code,
        bonus=bonus_val,
        total_referred=user.total_referred,
        bonuses=user.total_referred,
        saved=saved_val
    )
    
    ref_link = f"https://t.me/{bot_username}?start=REF_{user.referral_code}"
    keyboard = referral_keyboard(ref_link, user.language)
    
    # Orqaga qaytish tugmasini qo'shish
    keyboard.inline_keyboard.append(back_button(user.language).inline_keyboard[0])
    return text, keyboard


@router.message(Command("referral"))
async def referral_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        bot_info = await message.bot.get_me()
        text, keyboard = await get_referral_response(user, bot_info.username)
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "referral")
async def referral_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        bot_info = await callback.bot.get_me()
        text, keyboard = await get_referral_response(user, bot_info.username)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
