from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.queries import get_or_create_user, get_user_history, get_user_generation_count, AsyncSessionLocal
from bot.database.models import VideoGeneration
from bot.utils.messages import get_msg
from bot.keyboards.main import back_button

router = Router()


def get_history_gallery_keyboard(index: int, total: int, video_url: str) -> InlineKeyboardMarkup:
    """Oldingi videolar galereyasi uchun navigatsiya tugmalari"""
    buttons = [
        [
            InlineKeyboardButton(text="📤 Ulashish", switch_inline_query=f"AI orqali yaratgan videomni ko'ring! {video_url}"),
            InlineKeyboardButton(text="🔄 Qayta yasash", callback_data="video_start")
        ]
    ]
    
    # Sahifalash (Pagination) tugmalari
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"hist_view_{index - 1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="hist_page_info"))
    
    if index < total - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ▶️", callback_data=f"hist_view_{index + 1}"))
        
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="back_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "📋 Tarix")
@router.message(Command("history"))
async def history_message_handler(message: Message):
    await show_gallery_page(message, message.from_user.id, index=0, edit_mode=False)


@router.callback_query(F.data.startswith("history_"))
async def history_inline_callback_handler(callback: CallbackQuery):
    index = int(callback.data.split("_")[1])
    await show_gallery_page(callback.message, callback.from_user.id, index=index, edit_mode=True)
    await callback.answer()


@router.callback_query(F.data.startswith("hist_view_"))
async def history_callback_handler(callback: CallbackQuery):
    index = int(callback.data.split("_")[2])
    await show_gallery_page(callback.message, callback.from_user.id, index=index, edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "hist_page_info")
async def history_page_info_callback(callback: CallbackQuery):
    await callback.answer("Joriy sahifa / Jami videolar", show_alert=False)


async def show_gallery_page(message_obj: Message, user_id: int, index: int = 0, edit_mode: bool = False):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, user_id, None, None)
        user_lang = user.language
        
        # Jami muvaffaqiyatli videolarni bazadan olish
        from sqlalchemy import select, func, and_
        res_total = await session.execute(
            select(func.count(VideoGeneration.id)).where(
                and_(
                    VideoGeneration.user_id == user_id,
                    VideoGeneration.status == "done"
                )
            )
        )
        total = res_total.scalar_one()
        
        if total == 0:
            text = (
                "📋 <b>Sizda hali videolar yo'q.</b>\n\n"
                "🎬 Bosh menyudan <b>Video yaratish</b> tugmasini bosing!"
            )
            if edit_mode:
                await message_obj.edit_text(text, reply_markup=back_button(user_lang))
            else:
                await message_obj.answer(text, reply_markup=back_button(user_lang))
            return
            
        # Aniq indexdagi bitta videoni yuklash (offset=index, limit=1)
        res_video = await session.execute(
            select(VideoGeneration).where(
                and_(
                    VideoGeneration.user_id == user_id,
                    VideoGeneration.status == "done"
                )
            ).order_by(VideoGeneration.created_at.desc()).offset(index).limit(1)
        )
        video = res_video.scalar_one_or_none()
        
        if not video:
            await message_obj.answer("Video yuklashda xatolik yuz berdi.", reply_markup=back_button(user_lang))
            return
            
        # Caption matnini shakllantirish
        date_str = video.created_at.strftime("%d %B, %H:%M")
        caption = (
            "📋 <b>SIZNING VIDEOLARINGIZ</b>\n\n"
            f"🎬 <b>Video #{total - index}</b>\n"
            f"📝 <i>\"{video.prompt}\"</i>\n"
            f"📅 <b>Vaqt:</b> {date_str}\n"
            "🪙 <b>Narx:</b> 30 tanga\n\n"
            "⭐ @aivideochi_bot"
        )
        
        if edit_mode:
            # Silliq ishlashi uchun eski media xabarni o'chiramiz va yangisini yuboramiz
            try:
                await message_obj.delete()
            except Exception:
                pass
                
        try:
            await message_obj.answer_video(
                video=video.video_url,
                caption=caption,
                reply_markup=get_history_gallery_keyboard(index, total, video.video_url)
            )
        except Exception:
            # Fallback agar video ochilmasa
            fallback_text = (
                caption + f"\n\n🔗 <b>Yuklab olish havolasi:</b>\n{video.video_url}"
            )
            await message_obj.answer(
                fallback_text,
                reply_markup=get_history_gallery_keyboard(index, total, video.video_url)
            )
