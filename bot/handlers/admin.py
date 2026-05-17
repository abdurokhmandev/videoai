from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy import select, func, desc
from bot.database.models import User, VideoGeneration
from bot.database.queries import (
    get_or_create_user, get_user_count, get_new_users_today,
    get_today_video_count, get_today_revenue, get_all_users, AsyncSessionLocal,
    get_active_users, get_recent_payments, get_top_users
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
        
        try:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
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


@router.callback_query(F.data == "admin_users")
async def admin_users_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        # Foydalanuvchilar statistikasi
        total_u = await get_user_count(session)
        active_u = len(await get_active_users(session, days=30))
        
        # Blocked count
        blocked_res = await session.execute(select(func.count(User.id)).where(User.is_blocked == True))
        blocked_count = blocked_res.scalar_one()
        
        text = (
            "👥 <b>FOYDALANUVCHILAR STATISTIKASI</b>\n\n"
            f"📊 Jami foydalanuvchilar: <b>{total_u} ta</b>\n"
            f"⚡ Faol foydalanuvchilar (30 kun): <b>{active_u} ta</b>\n"
            f"🚫 Bloklanganlar: <b>{blocked_count} ta</b>\n"
        )
        
        try:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


@router.callback_query(F.data == "admin_payments")
async def admin_payments_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        # Oxirgi 10 ta to'lov
        recent_p = await get_recent_payments(session, limit=10)
        
        text = "💰 <b>OXIRGI TRANZAKSIYALAR (MAX 10 TA)</b>\n\n"
        if not recent_p:
            text += "Hozircha hech qanday tranzaksiyalar yo'q."
        else:
            from bot.utils.helpers import status_emoji
            for i, p in enumerate(recent_p, 1):
                emoji = status_emoji(p.status)
                date_str = p.created_at.strftime("%d.%m %H:%M")
                text += f"{i}. <code>ID:{p.id}</code> | <b>{p.amount:,} so'm</b> | {p.provider.upper()} | {p.package} | {emoji} | {date_str}\n"
                
        try:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


@router.callback_query(F.data == "admin_videos")
async def admin_videos_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        # Oxirgi 10 ta generatsiya
        from bot.utils.helpers import truncate_text, status_emoji
        
        res = await session.execute(
            select(VideoGeneration).order_by(desc(VideoGeneration.created_at)).limit(10)
        )
        recent_g = list(res.scalars().all())
        
        text = "🎬 <b>OXIRGI VIDEOLAR (MAX 10 TA)</b>\n\n"
        if not recent_g:
            text += "Hozircha hech qanday videolar yaratilmagan."
        else:
            for i, g in enumerate(recent_g, 1):
                emoji = status_emoji(g.status)
                date_str = g.created_at.strftime("%d.%m %H:%M")
                prompt_t = truncate_text(g.prompt, max_len=30)
                text += f"{i}. <code>U:{g.user_id}</code> | \"{prompt_t}\" | {g.api_provider} | {emoji} | {date_str}\n"
                
        try:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


@router.callback_query(F.data == "admin_top")
async def admin_top_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        # Top 10 foydalanuvchi
        top_u = await get_top_users(session, limit=10)
        
        text = "🏆 <b>TOP 10 FOYDALANUVCHILAR</b>\n\n"
        if not top_u:
            text += "Hozircha ma'lumot yo'q."
        else:
            for i, u in enumerate(top_u, 1):
                username_str = f"@{u.username}" if u.username else "no_username"
                text += f"{i}. <code>{u.id}</code> | <b>{u.full_name or 'Ismsiz'}</b> ({username_str}) | Jami: <b>{u.total_spent:,} so'm</b> ({u.total_videos} ta video)\n"
                
        try:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        await callback.answer()
