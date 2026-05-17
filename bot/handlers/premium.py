from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from bot.database.queries import get_or_create_user, deduct_tangas, AsyncSessionLocal
from bot.utils.messages import get_msg
from bot.keyboards.main import back_button

router = Router()


def get_premium_keyboard(is_active: bool) -> InlineKeyboardMarkup:
    buttons = []
    if not is_active:
        buttons.append([
            InlineKeyboardButton(text="💎 500 tangaga sotib olish", callback_data="buy_premium")
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("premium"))
async def premium_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        text = get_msg(user.language, "premium_info")
        
        if user.is_premium:
            until_str = user.premium_until.strftime("%d %B %Y")
            text += f"\n\n🏆 <b>Premium hisobingiz faol!</b>\nAmal qilish muddati: <b>{until_str}</b> gacha."
            
        await message.answer(text, reply_markup=get_premium_keyboard(user.is_premium))


@router.callback_query(F.data == "premium")
async def premium_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "premium_info")
        
        if user.is_premium:
            until_str = user.premium_until.strftime("%d %B %Y")
            text += f"\n\n🏆 <b>Premium hisobingiz faol!</b>\nAmal qilish muddati: <b>{until_str}</b> gacha."
            
        await callback.message.edit_text(text, reply_markup=get_premium_keyboard(user.is_premium))
        await callback.answer()


@router.callback_query(F.data == "buy_premium")
async def buy_premium_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        
        if user.is_premium:
            await callback.answer("Sizda Premium allaqachon faol!", show_alert=True)
            return
            
        if user.tangas < 500:
            await callback.answer("Premium olish uchun tangalaringiz yetarli emas! (Kamida 500 tanga zarur)", show_alert=True)
            return
            
        # 500 tanga yechib olish
        await deduct_tangas(session, user.id, 500)
        
        # Premium muddatini o'rnatish (30 kunga)
        user.is_premium = True
        user.premium_until = datetime.utcnow() + timedelta(days=30)
        await session.commit()
        
        success_text = (
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            "Siz muvaffaqiyatli <b>🏆 Premium obunachiga</b> aylandingiz!\n"
            "Barcha cheksiz imtiyozlar va kunlik bonuslar hozirdan boshlab faollashtirildi!"
        )
        await callback.message.edit_text(success_text, reply_markup=back_button(user.language))
        await callback.answer("Tabriklaymiz! Premium faollashdi! 🎉", show_alert=True)
