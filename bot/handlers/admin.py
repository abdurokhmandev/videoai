from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.queries import (
    get_or_create_user, get_user_count, get_new_users_today,
    get_today_video_count, get_today_revenue, get_all_users, AsyncSessionLocal
)
from bot.utils.messages import get_msg
from bot.keyboards.payment import admin_keyboard
from bot.keyboards.main import back_button
from bot.config import settings

router = Router()


class AdminState(StatesGroup):
    entering_broadcast = State()
    confirming_broadcast = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids_list


@router.message(Command("admin"))
async def admin_message_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Bu buyruq faqat adminlar uchun!")
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, message.from_user.id, None, None)
        
        # Admin ma'lumotlarini yuklash
        total_u = await get_user_count(session)
        new_today = await get_new_users_today(session)
        videos_today = await get_today_video_count(session)
        rev_today = await get_today_revenue(session)
        
        text = get_msg(user.language, "admin_panel").format(
            total_users=total_u,
            new_today=new_today,
            videos_today=videos_today,
            revenue_today=rev_today
        )
        
        await message.answer(text, reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        total_u = await get_user_count(session)
        new_today = await get_new_users_today(session)
        videos_today = await get_today_video_count(session)
        rev_today = await get_today_revenue(session)
        
        text = get_msg(user.language, "admin_panel").format(
            total_users=total_u,
            new_today=new_today,
            videos_today=videos_today,
            revenue_today=rev_today
        )
        
        await callback.message.edit_text(text, reply_markup=admin_keyboard())
        await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        await callback.message.edit_text(
            get_msg(user.language, "broadcast_ask"),
            reply_markup=back_button(user.language)
        )
        await state.set_state(AdminState.entering_broadcast)
        await callback.answer()


@router.message(AdminState.entering_broadcast)
async def admin_broadcast_entered(message: Message, state: FSMContext):
    broadcast_text = message.text
    await state.update_data(text=broadcast_text)
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, message.from_user.id, None, None)
        total_u = await get_user_count(session)
        
        text = get_msg(user.language, "broadcast_confirm").format(
            count=total_u,
            text=broadcast_text
        )
        
        # Tasdiqlash inline tugmasi
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, yuborilsin!", callback_data="broadcast_confirm_yes"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_stats")
            ]
        ])
        
        await message.answer(text, reply_markup=kb)
        await state.set_state(AdminState.confirming_broadcast)


@router.callback_query(AdminState.confirming_broadcast, F.data == "broadcast_confirm_yes")
async def admin_broadcast_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    broadcast_text = data.get("text")
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        all_users = await get_all_users(session)
        
        sent_count = 0
        total_count = len(all_users)
        
        await callback.message.edit_text("📢 Xabar yuborilmoqda... Iltimos kuting...")
        
        for u in all_users:
            try:
                await callback.bot.send_message(chat_id=u.id, text=broadcast_text)
                sent_count += 1
            except Exception:
                pass  # Agar user botni bloklagan bo'lsa
                
        done_text = get_msg(user.language, "broadcast_done").format(
            sent=sent_count,
            total=total_count
        )
        await callback.message.answer(done_text, reply_markup=back_button(user.language))
        await callback.answer("Broadcast yakunlandi!")
