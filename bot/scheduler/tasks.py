import logging
from datetime import datetime, timedelta, date
from aiogram import Bot
from sqlalchemy import select, and_

from bot.database.queries import AsyncSessionLocal, add_tangas
from bot.database.models import User
from bot.config import settings

logger = logging.getLogger(__name__)


async def run_daily_scheduler_tasks(bot: Bot):
    """
    Har kuni 20:00 da ishlaydigan scheduler tasklari.
    - Premium obuna taklifi (total_videos >= 2 bo'lgan va premium bo'lmaganlarga)
    - 3 kun kirmagan foydalanuvchilarga tanga bonus va bildirishnoma yuborish (Retention)
    - Premium tugash muddatlarini tekshirish
    """
    logger.info("Scheduler vazifalari ishga tushdi...")
    async with AsyncSessionLocal() as session:
        # 1. Premium obuna eslatmasi (2 ta video yasagan va eslatilmaganlarga)
        # Soddalik uchun total_videos == 2 bo'lgan va premium bo'lmaganlarni tanlaymiz (faqat 1 marta kelishi uchun)
        res_prem = await session.execute(
            select(User).where(
                and_(
                    User.total_videos == 2,
                    User.is_premium == False,
                    User.is_blocked == False
                )
            )
        )
        prem_candidates = res_prem.scalars().all()
        for u in prem_candidates:
            try:
                text = (
                    "👋 <b>Salom!</b>\n\n"
                    "Siz allaqachon 2 kun video yasayapsiz 🎬\n\n"
                    "🏆 <b>Premium bilan:</b>\n"
                    "• Har kuni +5 🪙 bepul tanga\n"
                    "• 2x tezroq generatsiya\n"
                    "• Watermark mutlaqo yo'q\n"
                    "• Priority navbat ustunligi\n\n"
                    "Bir oyda 150+ 🪙 tejaysiz! 💎"
                )
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏆 Premium olish", callback_data="premium")],
                    [InlineKeyboardButton(text="Keyinroq", callback_data="back_main")]
                ])
                await bot.send_message(chat_id=u.id, text=text, reply_markup=kb)
                logger.info(f"User {u.id} ga premium eslatmasi yuborildi.")
            except Exception as e:
                logger.error(f"User {u.id} ga premium eslatmasi yuborishda xato: {e}")

        # 2. 3 kun kirmagan foydalanuvchilar (Retention)
        cutoff = datetime.utcnow() - timedelta(days=3)
        res_inact = await session.execute(
            select(User).where(
                and_(
                    User.last_active <= cutoff,
                    User.is_blocked == False
                )
            )
        )
        inactive_users = res_inact.scalars().all()
        for u in inactive_users:
            try:
                # 10 tanga sovg'a qilish
                await add_tangas(session, u.id, 10)
                text = (
                    "👋 <b>Sog'indik!</b>\n\n"
                    "🎁 Sizga <b>+10 🪙 tanga</b> qo'shib qo'ydik!\n"
                    "Qani, yangi ajoyib video yasaymizmi? 🎬\n\n"
                    "Menyudan <b>🎬 Video yaratish</b> tugmasini bosing!"
                )
                await bot.send_message(chat_id=u.id, text=text)
                logger.info(f"User {u.id} ga retention xabari va 10 tanga berildi.")
            except Exception as e:
                logger.error(f"User {u.id} ga retention xabari yuborishda xato: {e}")

        # 3. Premium muddati tugaganlarni tekshirish va o'chirish
        now_time = datetime.utcnow()
        res_expired = await session.execute(
            select(User).where(
                and_(
                    User.is_premium == True,
                    User.premium_until <= now_time
                )
            )
        )
        expired_users = res_expired.scalars().all()
        for u in expired_users:
            try:
                u.is_premium = False
                u.premium_until = None
                await session.commit()
                await bot.send_message(
                    chat_id=u.id,
                    text="🏆 <b>Premium obunangiz muddati tugadi.</b> Sovg'alar va ustunliklarni davom ettirish uchun obunani yangilang!"
                )
                logger.info(f"User {u.id} premium obunasi o'chirildi (muddati tugagan).")
            except Exception as e:
                logger.error(f"User {u.id} premium o'chirishda xatolik: {e}")
                
        # 4. Premium obunachilarga kunlik +5 tanga sovg'asini tarqatish
        res_prem_active = await session.execute(
            select(User).where(
                and_(
                    User.is_premium == True,
                    User.is_blocked == False
                )
            )
        )
        active_premiums = res_prem_active.scalars().all()
        for u in active_premiums:
            try:
                await add_tangas(session, u.id, 5)
                await bot.send_message(
                    chat_id=u.id,
                    text="🎁 <b>Premium Kunlik Bonus!</b> Sizga bugun ham <b>+5 🪙 bepul tanga</b> berildi! Rahmat!"
                )
                logger.info(f"Premium User {u.id} ga kunlik +5 tanga berildi.")
            except Exception as e:
                logger.error(f"Premium User {u.id} kunlik tanga bonusida xato: {e}")
