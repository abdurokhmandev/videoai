from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import get_or_create_user, get_referral_stats, AsyncSessionLocal
from bot.utils.messages import get_msg
from bot.keyboards.main import referral_keyboard, back_button
from bot.config import settings

router = Router()


async def get_referral_response(session, user, bot_username: str):
    stats = await get_referral_stats(session, user.id)
    total_referred = stats["total_referred"]
    bonuses_given = stats["bonuses_given"]
    
    # +20 tanga sovg'a
    text = get_msg(user.language, "referral_info").format(
        bot_username=bot_username,
        ref_code=user.referral_code,
        total_referred=total_referred,
        bonuses=bonuses_given * 20
    )
    
    ref_link = f"https://t.me/{bot_username}?start=REF_{user.referral_code}"
    keyboard = referral_keyboard(ref_link, user.language)
    keyboard.inline_keyboard.append(back_button(user.language).inline_keyboard[0])
    return text, keyboard


@router.message(F.text == "👥 Do'stlar")
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
        text, keyboard = await get_referral_response(session, user, bot_info.username)
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
        text, keyboard = await get_referral_response(session, user, bot_info.username)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


@router.callback_query(F.data == "ref_details")
async def ref_details_callback(callback: CallbackQuery):
    await callback.answer(
        "Taklif qilingan do'stingiz birinchi marta botni ishga tushirishi bilan sizga ham, unga ham +20 tanga avtomatik qo'shiladi!",
        show_alert=True
    )
