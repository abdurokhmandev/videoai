import asyncio
from decimal import Decimal
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.queries import (
    get_or_create_user, create_generation, complete_generation,
    deduct_balance, fail_generation, update_user_stats, AsyncSessionLocal
)
from bot.utils.messages import get_msg
from bot.keyboards.video import model_select_keyboard, confirm_video_keyboard
from bot.keyboards.main import back_button, after_video_keyboard
from bot.utils.helpers import check_nsfw, make_progress_bar
from bot.config import settings

router = Router()


class VideoState(StatesGroup):
    selecting_model = State()
    entering_prompt = State()
    confirming = State()


@router.message(Command("video"))
async def video_message_handler(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        # Balans tekshirish (eng arzon model uchun)
        if user.balance < settings.FAST_VIDEO_PRICE:
            text = get_msg(user.language, "balance_low").format(
                needed=settings.FAST_VIDEO_PRICE,
                balance=user.balance
            )
            await message.answer(text, reply_markup=back_button(user.language))
            return
            
        text = get_msg(user.language, "select_model").format(
            fast_price=settings.FAST_VIDEO_PRICE,
            premium_price=settings.PREMIUM_VIDEO_PRICE
        )
        await message.answer(text, reply_markup=model_select_keyboard(user.language))
        await state.set_state(VideoState.selecting_model)


@router.callback_query(F.data == "video_start")
async def video_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        if user.balance < settings.FAST_VIDEO_PRICE:
            text = get_msg(user.language, "balance_low").format(
                needed=settings.FAST_VIDEO_PRICE,
                balance=user.balance
            )
            await callback.message.edit_text(text, reply_markup=back_button(user.language))
            await callback.answer()
            return
            
        text = get_msg(user.language, "select_model").format(
            fast_price=settings.FAST_VIDEO_PRICE,
            premium_price=settings.PREMIUM_VIDEO_PRICE
        )
        await callback.message.edit_text(text, reply_markup=model_select_keyboard(user.language))
        await state.set_state(VideoState.selecting_model)
        await callback.answer()


@router.callback_query(VideoState.selecting_model, F.data.startswith("model_"))
async def model_selected_handler(callback: CallbackQuery, state: FSMContext):
    model = callback.data.split("_")[1]
    await state.update_data(model=model)
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "enter_prompt")
        await callback.message.edit_text(text, reply_markup=back_button(user.language))
        await state.set_state(VideoState.entering_prompt)
        await callback.answer()


@router.message(VideoState.entering_prompt)
async def prompt_entered_handler(message: Message, state: FSMContext):
    prompt = message.text.strip()
    
    # NSFW tekshiruvi
    if check_nsfw(prompt):
        async with AsyncSessionLocal() as session:
            user, _ = await get_or_create_user(session, message.from_user.id, None, None)
            await message.answer(get_msg(user.language, "nsfw_blocked"), reply_markup=back_button(user.language))
        return

    data = await state.get_data()
    model = data.get("model", "fast")
    price = settings.FAST_VIDEO_PRICE if model == "fast" else settings.PREMIUM_VIDEO_PRICE
    model_name = "⚡ Tezkor" if model == "fast" else "🏆 Premium"
    
    await state.update_data(prompt=prompt)
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        # Balans yetarliligini qayta tekshirish
        if user.balance < price:
            text = get_msg(user.language, "balance_low").format(needed=price, balance=user.balance)
            await message.answer(text, reply_markup=back_button(user.language))
            return
            
        new_balance = user.balance - Decimal(str(price))
        text = get_msg(user.language, "confirm_video").format(
            prompt=prompt,
            model_name=model_name,
            cost=price,
            balance=user.balance,
            new_balance=new_balance
        )
        
        await message.answer(text, reply_markup=confirm_video_keyboard(user.language))
        await state.set_state(VideoState.confirming)


@router.callback_query(VideoState.confirming, F.data == "video_confirm")
async def video_confirm_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    model = data.get("model", "fast")
    prompt = data.get("prompt")
    
    price = settings.FAST_VIDEO_PRICE if model == "fast" else settings.PREMIUM_VIDEO_PRICE
    provider = "siliconflow" if model == "fast" else "atlascloud"
    
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        user_lang = user.language
        
        if user.balance < price:
            text = get_msg(user_lang, "balance_low").format(needed=price, balance=user.balance)
            await callback.message.edit_text(text, reply_markup=back_button(user_lang))
            await callback.answer()
            return
            
        # Balansdan yechib olish
        await deduct_balance(session, user.id, Decimal(str(price)))
        
        # Generatsiya ob'ektini yaratish
        generation = await create_generation(
            session=session,
            user_id=user.id,
            prompt=prompt,
            api_provider=provider,
            cost_som=Decimal(str(price))
        )
        
        await callback.answer("Video generatsiya boshlandi!")
        
        # Yuklanish progress barini yuborish
        time_needed = 10 if model == "fast" else 15
        progress_msg = await callback.message.edit_text(
            get_msg(user_lang, "generation_started").format(time=time_needed)
        )
        
        # Dinamik Progress Bar simulatsiyasi (o'ta professional effekt)
        for percent in range(10, 101, 20):
            await asyncio.sleep(2)
            bar = make_progress_bar(percent, length=10)
            remaining = int(time_needed * (100 - percent) / 100)
            try:
                await progress_msg.edit_text(
                    get_msg(user_lang, "generation_progress").format(
                        bar=bar,
                        percent=percent,
                        remaining=remaining
                    )
                )
            except Exception:
                pass
                
        # Generatsiyani yakunlash (Simulyatsiya uchun bitta tayyor chiroyli video linki)
        # Haqiqiy API-ni ulasangiz, bu yerda SiliconFlow yoki AtlasCloud xizmati chaqiriladi
        sample_video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        
        await complete_generation(session, generation.id, sample_video_url, "job_test_1234")
        await update_user_stats(session, user.id, Decimal(str(price)))
        
        # Foydalanuvchini oxirgi balansini olish
        await session.refresh(user)
        
        # Yakuniy xabarni chiqarish
        done_text = get_msg(user_lang, "generation_done").format(
            prompt=prompt,
            duration=time_needed,
            cost=price,
            balance=user.balance
        )
        
        await callback.message.delete()
        
        try:
            await callback.message.answer_video(
                video=sample_video_url,
                caption=done_text,
                reply_markup=after_video_keyboard(user_lang)
            )
        except Exception:
            # Agar Telegram serveri video URLni tortolmasa, fallback havola bilan chiroyli matn yuboramiz
            fallback_text = done_text + f"\n\n🔗 <b>Video yuklab olish havolasi:</b>\n{sample_video_url}"
            await callback.message.answer(
                fallback_text,
                reply_markup=after_video_keyboard(user_lang)
            )
