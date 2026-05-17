import asyncio
from decimal import Decimal
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.queries import (
    get_or_create_user, create_generation, complete_generation,
    deduct_tangas, fail_generation, update_user_stats, 
    increment_streak, add_tangas, AsyncSessionLocal
)
from bot.utils.messages import get_msg
from bot.keyboards.video import confirm_video_keyboard
from bot.keyboards.main import back_button, after_video_keyboard
from bot.keyboards.payment import balance_low_keyboard
from bot.utils.helpers import check_nsfw, make_progress_bar
from bot.config import settings
from bot.services.fal_api import generate_video

router = Router()


class VideoState(StatesGroup):
    entering_prompt = State()
    confirming = State()


@router.message(F.text == "🎬 Video yaratish")
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
        
        # Balans tekshirish (kamida 30 tanga)
        if user.tangas < 30:
            text = get_msg(user.language, "balance_low").format(
                needed=30 - user.tangas,
                balance=user.tangas
            )
            await message.answer(text, reply_markup=balance_low_keyboard())
            return
            
        text = get_msg(user.language, "enter_prompt").format(
            balance=user.tangas
        )
        await message.answer(text, reply_markup=back_button(user.language))
        await state.set_state(VideoState.entering_prompt)


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
        
        if user.tangas < 30:
            text = get_msg(user.language, "balance_low").format(
                needed=30 - user.tangas,
                balance=user.tangas
            )
            await callback.message.edit_text(text, reply_markup=balance_low_keyboard())
            await callback.answer()
            return
            
        text = get_msg(user.language, "enter_prompt").format(
            balance=user.tangas
        )
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

    await state.update_data(prompt=prompt)
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        # Balans yetarliligini qayta tekshirish
        if user.tangas < 30:
            text = get_msg(user.language, "balance_low").format(
                needed=30 - user.tangas,
                balance=user.tangas
            )
            await message.answer(text, reply_markup=balance_low_keyboard())
            return
            
        new_balance = user.tangas - 30
        text = get_msg(user.language, "confirm_video").format(
            prompt=prompt,
            balance=user.tangas,
            new_balance=new_balance
        )
        
        await message.answer(text, reply_markup=confirm_video_keyboard(user.language))
        await state.set_state(VideoState.confirming)


@router.callback_query(VideoState.confirming, F.data == "video_edit_prompt")
async def video_edit_prompt_handler(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        text = get_msg(user.language, "enter_prompt").format(balance=user.tangas)
        await callback.message.edit_text(text, reply_markup=back_button(user.language))
        await state.set_state(VideoState.entering_prompt)
        await callback.answer()


@router.callback_query(VideoState.confirming, F.data == "video_confirm")
async def video_confirm_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prompt = data.get("prompt")
    
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        user_lang = user.language
        
        if user.tangas < 30:
            text = get_msg(user_lang, "balance_low").format(
                needed=30 - user.tangas,
                balance=user.tangas
            )
            await callback.message.edit_text(text, reply_markup=balance_low_keyboard())
            await callback.answer()
            return
            
        # Balansdan tangalarni yechib olish
        await deduct_tangas(session, user.id, 30)
        
        # Generatsiya ob'ektini yaratish
        generation = await create_generation(
            session=session,
            user_id=user.id,
            prompt=prompt,
            api_provider="fal.ai",
            cost_tangas=30
        )
        
        await callback.answer("Video generatsiya boshlandi!")
        
        # Yuklanish progress barini yuborish
        time_needed = 20
        progress_msg = await callback.message.edit_text(
            get_msg(user_lang, "generation_started").format(time=time_needed)
        )
        
        # Dinamik Progress Bar simulatsiyasi (o'ta professional effekt)
        for percent in range(10, 101, 20):
            await asyncio.sleep(2.5)
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
                
        # Haqiqiy Fal.ai API ulanishi chaqiriladi
        video_url = await generate_video(prompt)
        
        await complete_generation(session, generation.id, video_url, "job_fal_" + str(generation.id))
        await update_user_stats(session, user.id, 30)
        
        # Streak tizimini tekshirish va oshirish
        streak = await increment_streak(session, user.id)
        if streak > 0:
            if streak == 7:
                await add_tangas(session, user.id, 10)
                await callback.message.answer(
                    "🔥 <b>7 kunlik streak!</b>\n\n"
                    "Zo'r! Siz 7 kun ketma-ket video yaratdingiz!\n"
                    "🎁 <b>+10 🪙 bonus tanga</b> berildi!\n\n"
                    "Davom eting! 💪"
                )
            elif streak % 3 == 0:
                await add_tangas(session, user.id, 2)
                await callback.message.answer(
                    f"🔥 <b>{streak} kunlik streak!</b>\n\n"
                    "Bugun ham video yaratdingiz! <b>+2 🪙 bonus tanga</b>\n"
                    "Ertaga ham keling — streak davom etsin!"
                )
        
        # Foydalanuvchini oxirgi balansini olish
        await session.refresh(user)
        
        # Yakuniy xabarni chiqarish
        done_text = get_msg(user_lang, "generation_done").format(
            prompt=prompt,
            duration=time_needed,
            balance=user.tangas
        )
        
        # Watermark matnini captionga biriktiramiz
        done_text += "\n\n⭐ <b>Hamkor:</b> @aivideochi_bot"
        
        await callback.message.delete()
        
        try:
            await callback.message.answer_video(
                video=video_url,
                caption=done_text,
                reply_markup=after_video_keyboard(user_lang)
            )
        except Exception:
            # Fallback
            fallback_text = done_text + f"\n\n🔗 <b>Video yuklab olish havolasi:</b>\n{video_url}"
            await callback.message.answer(
                fallback_text,
                reply_markup=after_video_keyboard(user_lang)
            )
