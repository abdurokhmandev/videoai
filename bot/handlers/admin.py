from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy import select, func, desc
from bot.database.models import User, VideoGeneration, Payment
from bot.database.queries import (
    get_or_create_user, get_user_count, get_new_users_today,
    get_today_video_count, get_today_revenue, get_all_users, AsyncSessionLocal,
    get_active_users, get_recent_payments, get_top_users,
    confirm_manual_payment, get_payment
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
        rev_today = await get_today_revenue(session)  # Bugungi so'm daromad
        
        text = (
            "👑 <b>ADMIN PANEL</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>Bugungi statistika:</b>\n"
            f"👥 Jami userlar: <b>{total_u} ta</b>\n"
            f"🆕 Bugun yangilar: <b>{new_today} ta</b>\n"
            f"🎬 Bugun videolar: <b>{videos_today} ta</b>\n"
            f"💰 Bugun daromad: <b>{rev_today:,} so'm</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        
        await message.answer(text, reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        total_u = await get_user_count(session)
        new_today = await get_new_users_today(session)
        videos_today = await get_today_video_count(session)
        rev_today = await get_today_revenue(session)
        
        text = (
            "👑 <b>ADMIN PANEL</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>Bugungi statistika:</b>\n"
            f"👥 Jami userlar: <b>{total_u} ta</b>\n"
            f"🆕 Bugun yangilar: <b>{new_today} ta</b>\n"
            f"🎬 Bugun videolar: <b>{videos_today} ta</b>\n"
            f"💰 Bugun daromad: <b>{rev_today:,} so'm</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
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
    # Xabarning message_id va chat_id sini saqlaymiz (copy_message uchun)
    await state.update_data(
        broadcast_message_id=message.message_id,
        broadcast_chat_id=message.chat.id
    )
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, message.from_user.id, None, None)
        total_u = await get_user_count(session)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, yuborilsin!", callback_data="broadcast_confirm_yes"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_stats")
            ]
        ])
        
        preview_text = (
            f"📢 <b>BROADCAST PREVIEW (XABAR KO'RINISHI)</b>\n\n"
            f"Ushbu xabar jami <b>{total_u} ta</b> faol foydalanuvchiga yuboriladi.\n"
            f"Quyida xabarning aynan o'zi ko'rsatilgan, tasdiqlash uchun yashil tugmani bosing 👇"
        )
        await message.answer(preview_text)
        
        # Xabarni nusxasini yuborib preview qilamiz
        await message.copy_to(chat_id=message.chat.id, reply_markup=kb)
        await state.set_state(AdminState.confirming_broadcast)


@router.callback_query(AdminState.confirming_broadcast, F.data == "broadcast_confirm_yes")
async def admin_broadcast_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("broadcast_message_id")
    chat_id = data.get("broadcast_chat_id")
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        all_users = await get_all_users(session)
        
        sent_count = 0
        total_count = len(all_users)
        
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        status_msg = await callback.message.answer("📢 Xabar yuborilmoqda... Iltimos kuting...")
        
        for u in all_users:
            try:
                await callback.bot.copy_message(
                    chat_id=u.id,
                    from_chat_id=chat_id,
                    message_id=msg_id
                )
                sent_count += 1
            except Exception:
                pass
                
        try:
            await status_msg.delete()
        except Exception:
            pass
            
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
        total_u = await get_user_count(session)
        active_u = len(await get_active_users(session, days=30))
        
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
        recent_p = await get_recent_payments(session, limit=10)
        
        text = "💰 <b>OXIRGI TRANZAKSIYALAR (MAX 10 TA)</b>\n\n"
        if not recent_p:
            text += "Hozircha hech qanday tranzaksiyalar yo'q."
        else:
            from bot.utils.helpers import status_emoji
            for i, p in enumerate(recent_p, 1):
                emoji = status_emoji(p.status)
                date_str = p.created_at.strftime("%d.%m %H:%M")
                text += f"{i}. <code>ID:{p.id}</code> | <b>{p.amount_tangas} tanga</b> | {p.provider.upper()} | {p.package} | {emoji} | {date_str}\n"
                
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
                date_str = g.created_at.strftime("%d.%m Kecha" if g.created_at.date() == datetime.utcnow().date() else "%d.%m %H:%M")
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
        top_u = await get_top_users(session, limit=10)
        
        text = "🏆 <b>TOP 10 FOYDALANUVCHILAR</b>\n\n"
        if not top_u:
            text += "Hozircha ma'lumot yo'q."
        else:
            for i, u in enumerate(top_u, 1):
                username_str = f"@{u.username}" if u.username else "no_username"
                text += f"{i}. <code>{u.id}</code> | <b>{u.full_name or 'Ismsiz'}</b> ({username_str}) | Jami: <b>{u.total_spent} 🪙</b> ({u.total_videos} ta video)\n"
                
        try:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


# ─── ADMIN CONFIRM / REJECT MANUAL PAYMENTS ────────────────────────────────────

@router.callback_query(F.data.startswith("admin_confirm_pay_"))
async def admin_confirm_payment_handler(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    payment_id = int(callback.data.split("_")[3])
    
    async with AsyncSessionLocal() as session:
        payment = await get_payment(session, payment_id)
        if not payment:
            await callback.answer("To'lov topilmadi!", show_alert=True)
            return
            
        if payment.status == "confirmed":
            await callback.answer("Bu to'lov allaqachon tasdiqlangan!", show_alert=True)
            return
            
        # To'lovni tasdiqlash (tanga qo'shish bilan birga)
        payment, referrer_id, bonus_amount = await confirm_manual_payment(session, payment_id)
        
        if referrer_id and bonus_amount > 0:
            try:
                from bot.database.queries import get_user
                referred_user = await get_user(session, payment.user_id)
                friend_name = referred_user.full_name or "Do'stingiz" if referred_user else "Do'stingiz"
                ref_text = (
                    "🎁 <b>Do'stingiz tanga sotib oldi!</b>\n\n"
                    f"{friend_name} taklif havolangiz orqali kirib, tanga sotib oldi.\n"
                    f"Sizga <b>+{bonus_amount} 🪙 bonus tanga</b> taqdim etildi!"
                )
                await callback.bot.send_message(chat_id=referrer_id, text=ref_text)
            except Exception:
                pass
        
        # Foydalanuvchini xabardor qilish
        try:
            text_to_user = (
                "🎉 <b>Karta orqali to'lovingiz tasdiqlandi!</b>\n\n"
                f"🪙 <b>+{payment.amount_tangas} tanga</b> hisobingizga qo'shildi. Rahmat! 🙏"
            )
            await callback.bot.send_message(chat_id=payment.user_id, text=text_to_user)
        except Exception:
            pass
            
        # Admin xabarini yangilash
        new_caption = (
            callback.message.caption + 
            f"\n\n✅ <b>TASDIQLANDI!</b>\nAdmin: @{callback.from_user.username or 'ID:' + str(callback.from_user.id)}"
        )
        await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        await callback.answer("To'lov muvaffaqiyatli tasdiqlandi! ✅", show_alert=True)


@router.callback_query(F.data.startswith("admin_reject_pay_"))
async def admin_reject_payment_handler(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
        
    payment_id = int(callback.data.split("_")[3])
    
    async with AsyncSessionLocal() as session:
        payment = await get_payment(session, payment_id)
        if not payment:
            await callback.answer("To'lov topilmadi!", show_alert=True)
            return
            
        if payment.status != "pending":
            await callback.answer("Faqat kutilayotgan to'lovni rad etish mumkin!", show_alert=True)
            return
            
        payment.status = "cancelled"
        await session.commit()
        
        # Foydalanuvchini xabardor qilish
        try:
            text_to_user = (
                "❌ <b>Afsuski, yuborgan to'lov chekingiz adminlar tomonidan rad etildi.</b>\n\n"
                "Iltimos, o'tkazma tafsilotlarini qayta tekshiring yoki adminga murojaat qiling."
            )
            await callback.bot.send_message(chat_id=payment.user_id, text=text_to_user)
        except Exception:
            pass
            
        # Admin xabarini yangilash
        new_caption = (
            callback.message.caption + 
            f"\n\n❌ <b>RAD ETILDI!</b>\nAdmin: @{callback.from_user.username or 'ID:' + str(callback.from_user.id)}"
        )
        await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        await callback.answer("To'lov rad etildi! ❌", show_alert=True)
