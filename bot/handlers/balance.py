from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import get_or_create_user, AsyncSessionLocal
from bot.utils.messages import get_msg
from bot.keyboards.main import balance_keyboard, back_button
from bot.keyboards.payment import packages_keyboard, payment_methods_keyboard
from bot.config import settings

router = Router()


@router.message(F.text == "🪙 Balans")
@router.message(Command("balance"))
async def balance_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        text = get_msg(user.language, "balance_info").format(
            balance=user.tangas,
            total_videos=user.total_videos,
            streak=user.streak_days,
            created=user.created_at.strftime("%d %b %Y")
        )
        
        await message.answer(text, reply_markup=balance_keyboard(user.language))


@router.callback_query(F.data == "balance")
async def balance_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "balance_info").format(
            balance=user.tangas,
            total_videos=user.total_videos,
            streak=user.streak_days,
            created=user.created_at.strftime("%d %b %Y")
        )
        
        await callback.message.edit_text(text, reply_markup=balance_keyboard(user.language))
        await callback.answer()


@router.message(F.text == "🪙 Tanga olish")
@router.message(Command("topup"))
async def topup_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        text = get_msg(user.language, "topup_menu").format(
            balance=user.tangas
        )
        await message.answer(text, reply_markup=packages_keyboard())


@router.callback_query(F.data == "topup")
async def topup_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "topup_menu").format(
            balance=user.tangas
        )
        await callback.message.edit_text(text, reply_markup=packages_keyboard())
        await callback.answer()


@router.callback_query(F.data.startswith("pkg_"))
async def package_selected_handler(callback: CallbackQuery):
    package_key = callback.data.split("_")[1]
    pkg_data = settings.packages.get(package_key)
    
    if not pkg_data:
        await callback.answer("Paket topilmadi!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        text = get_msg(user.language, "topup_details").format(
            package_name=pkg_data["name"],
            tangas=pkg_data["tangas"]
        )
        await callback.message.edit_text(
            text, 
            reply_markup=payment_methods_keyboard(package_key)
        )
        await callback.answer()
