import asyncio
import os
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
from bot.keyboards.video import (
    model_select_keyboard, mode_select_keyboard,
    video_details_keyboard, confirm_video_keyboard
)
from bot.keyboards.main import back_button, after_video_keyboard
from bot.keyboards.payment import balance_low_keyboard
from bot.utils.helpers import check_nsfw, make_progress_bar
from bot.config import settings
from bot.services.fal_api import generate_video

router = Router()

class VideoState(StatesGroup):
    selecting_model = State()  # Fast vs Best
    selecting_mode = State()   # Text vs Image
    showing_details = State()  # Sample video & stats
    entering_image = State()   # Asking for image (optional)
    entering_prompt = State()  # Asking for prompt text
    confirming = State()       # Final preview

# 🎬 Video Yaratish Boshlanishi (Text or Command)
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
        
        # Har qanday holatda minimal balans 15 tanga bo'lishi kerak
        if user.tangas < 15:
            text = get_msg(user.language, "balance_low").format(
                needed=15 - user.tangas,
                balance=user.tangas
            )
            await message.answer(text, reply_markup=balance_low_keyboard())
            return
            
        text = (
            "🎬 <b>AI VIDEO YARATISH BO'LIMI</b>\n\n"
            "Ushbu bo'limda siz istalgan matn yoki rasm asosida ajoyib videolar yaratishingiz mumkin! 🚀\n\n"
            "Iltimos, ishlatmoqchi bo'lgan **AI modelingizni tanlang** 👇"
        )
        await message.answer(text, reply_markup=model_select_keyboard())
        await state.set_state(VideoState.selecting_model)

# Callback orqali boshlash (Asosiy menyudan)
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
        
        if user.tangas < 15:
            text = get_msg(user.language, "balance_low").format(
                needed=15 - user.tangas,
                balance=user.tangas
            )
            await callback.message.edit_text(text, reply_markup=balance_low_keyboard())
            await callback.answer()
            return
            
        text = (
            "🎬 <b>AI VIDEO YARATISH BO'LIMI</b>\n\n"
            "Ushbu bo'limda siz istalgan matn yoki rasm asosida ajoyib videolar yaratishingiz mumkin! 🚀\n\n"
            "Iltimos, ishlatmoqchi bo'lgan **AI modelingizni tanlang** 👇"
        )
        await callback.message.edit_text(text, reply_markup=model_select_keyboard())
        await state.set_state(VideoState.selecting_model)
        await callback.answer()

# 1. Model Tanlanganda (Fast yoki Best)
@router.callback_query(VideoState.selecting_model, F.data.startswith("select_model_"))
async def model_selected_handler(callback: CallbackQuery, state: FSMContext):
    model = callback.data.split("_")[2] # fast yoki best
    await state.update_data(model_type=model)
    
    model_name = "⚡ Tezkor AI (Wan v2.1)" if model == "fast" else "💎 Premium AI (Luma Dream)"
    text = (
        f"🤖 <b>Tanlangan model:</b> {model_name}\n\n"
        "Videoni qanday rejimda yaratmoqchisiz? 👇"
    )
    await callback.message.edit_text(text, reply_markup=mode_select_keyboard())
    await state.set_state(VideoState.selecting_mode)
    await callback.answer()

# 2. Rejim Tanlanganda (Text yoki Image)
@router.callback_query(VideoState.selecting_mode, F.data.startswith("select_mode_"))
async def mode_selected_handler(callback: CallbackQuery, state: FSMContext):
    mode = callback.data.split("_")[2] # text yoki image
    await state.update_data(mode=mode)
    
    data = await state.get_data()
    model = data.get("model_type")
    
    # Namunaviy video va parametrlar tafsiloti
    if model == "best":
        model_title = "💎 Premium AI (Luma Dream Machine)"
        cost = 30
        duration = 5
        quality = "1080p Full HD"
        time_est = "~20-30 soniya"
        sample_video = "https://cdn.pixabay.com/video/2023/10/21/185934-877202302_large.mp4" # Professional premium misol
    else:
        model_title = "⚡ Tezkor AI (Wan v2.1)"
        cost = 15
        duration = 5
        quality = "720p HD"
        time_est = "~10-15 soniya"
        sample_video = "https://cdn.pixabay.com/video/2024/02/09/200007-911894273_large.mp4" # Tezkor model misoli

    mode_title = "Matn orqali (Text-to-Video)" if mode == "text" else "Rasm + Matn orqali (Image-to-Video)"
    
    caption = (
        f"📊 <b>AI VIDEO TAVSIFI & SIFATI</b>\n\n"
        f"🤖 <b>Model:</b> {model_title}\n"
        f"⚙️ <b>Rejim:</b> {mode_title}\n"
        f"✨ <b>Sifat:</b> {quality}\n"
        f"⏱️ <b>Davomiyligi:</b> {duration} soniya\n"
        f"⏳ <b>Yaratilish vaqti:</b> {time_est}\n"
        f"🪙 <b>Narxi:</b> {cost} tanga\n\n"
        "🎬 Quyida ushbu model yaratgan namunaviy video taqdim etilgan 👇"
    )
    
    # Eski xabarni o'chirib, namunaviy video bilan yangi xabar yuboramiz
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer_video(
        video=sample_video,
        caption=caption,
        reply_markup=video_details_keyboard()
    )
    await state.set_state(VideoState.showing_details)
    await callback.answer()

# Orqaga qaytish (Rejimdan modelga)
@router.callback_query(VideoState.selecting_mode, F.data == "video_start")
async def back_to_model_callback(callback: CallbackQuery, state: FSMContext):
    await video_callback_handler(callback, state)

# Orqaga qaytish (Namunadan rejimga)
@router.callback_query(VideoState.showing_details, F.data == "video_select_mode")
async def back_to_mode_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    model = data.get("model_type")
    
    # Eski namunaviy video xabarni o'chiramiz
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    model_name = "⚡ Tezkor AI (Wan v2.1)" if model == "fast" else "💎 Premium AI (Luma Dream)"
    text = (
        f"🤖 <b>Tanlangan model:</b> {model_name}\n\n"
        "Videoni qanday rejimda yaratmoqchisiz? 👇"
    )
    await callback.message.answer(text, reply_markup=mode_select_keyboard())
    await state.set_state(VideoState.selecting_mode)
    await callback.answer()

# 3. Namunadan keyin Yaratish bosilganda
@router.callback_query(VideoState.showing_details, F.data == "details_confirm")
async def details_confirmed_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mode")
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    if mode == "image":
        text = (
            "🖼️ <b>Iltimos, video yaratish uchun rasm yuboring:</b>\n\n"
            "Rasm formati istalgancha (JPEG, PNG) bo'lishi mumkin. "
            "Rasm yuborilgach, unga tegishli prompt so'raladi."
        )
        await callback.message.answer(text, reply_markup=back_button())
        await state.set_state(VideoState.entering_image)
    else:
        text = (
            "📝 <b>Iltimos, video uchun matnli prompt kiriting:</b>\n\n"
            "Matnni o'zbek yoki ingliz tilida yozishingiz mumkin. "
            "Batafsilroq tasvirlash yanada ajoyib natija beradi!"
        )
        await callback.message.answer(text, reply_markup=back_button())
        await state.set_state(VideoState.entering_prompt)
    await callback.answer()

# 4. Rasm yuborilganda (Faqat Image rejimda)
@router.message(VideoState.entering_image, F.photo)
async def image_received_handler(message: Message, state: FSMContext):
    photo = message.photo[-1] # Eng katta o'lchamdagi rasm
    
    # Rasmni yuklab olish
    os.makedirs("artifacts/temp_uploads", exist_ok=True)
    file_path = f"artifacts/temp_uploads/{photo.file_id}.jpg"
    
    wait_msg = await message.answer("📥 Rasm yuklab olinmoqda...")
    try:
        file = await message.bot.get_file(photo.file_id)
        await message.bot.download_file(file.file_path, file_path)
        await state.update_data(image_path=file_path)
        
        await wait_msg.delete()
        await message.answer(
            "📝 <b>Rasm qabul qilindi!</b>\n\n"
            "Endi ushbu rasm qanday harakatlanishi haqida matnli prompt yuboring:"
        )
        await state.set_state(VideoState.entering_prompt)
    except Exception as e:
        await wait_msg.edit_text("❌ Rasmni yuklab olishda xatolik yuz berdi. Iltimos qaytadan yuboring:")

@router.message(VideoState.entering_image)
async def image_invalid_handler(message: Message):
    await message.answer("⚠️ Iltimos, faqat rasm (photo) formatida fayl yuboring:")

# 5. Prompt Matni yuborilganda
@router.message(VideoState.entering_prompt, F.text)
async def prompt_received_handler(message: Message, state: FSMContext):
    prompt = message.text.strip()
    
    # NSFW Tekshiruvi
    if check_nsfw(prompt):
        await message.answer("⚠️ Prompt ichida nojo'ya (NSFW) so'zlar aniqlandi. Iltimos, boshqa matn kiriting:")
        return
        
    await state.update_data(prompt=prompt)
    
    data = await state.get_data()
    model = data.get("model_type")
    mode = data.get("mode")
    cost = 30 if model == "best" else 15
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, message.from_user.id, None, None)
        
        # Balans yetarliligini tekshirish
        if user.tangas < cost:
            text = get_msg(user.language, "balance_low").format(
                needed=cost - user.tangas,
                balance=user.tangas
            )
            await message.answer(text, reply_markup=balance_low_keyboard())
            return
            
        new_balance = user.tangas - cost
        model_title = "💎 Premium AI (Luma)" if model == "best" else "⚡ Tezkor AI (Wan)"
        mode_title = "Matn" if mode == "text" else "Rasm + Matn"
        
        text = (
            "📋 <b>BUYURTMA TAFSILOTLARI</b>\n\n"
            f"🤖 <b>AI Model:</b> {model_title}\n"
            f"⚙️ <b>Rejim:</b> {mode_title}\n"
            f"📝 <b>Prompt:</b> <i>\"{prompt}\"</i>\n"
            f"🪙 <b>Sarflanadigan tanga:</b> {cost} ta\n"
            f"💳 Joriy balans: <b>{user.tangas} ta</b>\n"
            f"💰 Qoladigan balans: <b>{new_balance} ta</b>\n\n"
            "Tasdiqlaysizmi? 👇"
        )
        await message.answer(text, reply_markup=confirm_video_keyboard(user.language))
        await state.set_state(VideoState.confirming)

@router.message(VideoState.entering_prompt)
async def prompt_invalid_handler(message: Message):
    await message.answer("⚠️ Iltimos, faqat matnli prompt kiriting:")

# Prompt tahrirlash
@router.callback_query(VideoState.confirming, F.data == "video_edit_prompt")
async def video_edit_prompt_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mode")
    
    if mode == "image":
        text = "🖼️ <b>Yangi rasm yuboring:</b>"
        await callback.message.edit_text(text, reply_markup=back_button())
        await state.set_state(VideoState.entering_image)
    else:
        text = "📝 <b>Yangi prompt matnini kiriting:</b>"
        await callback.message.edit_text(text, reply_markup=back_button())
        await state.set_state(VideoState.entering_prompt)
    await callback.answer()

# 6. Yakuniy Yaratish Bosilganda va Deferred Billing (To'lov renderdan so'ng yechiladi)
@router.callback_query(VideoState.confirming, F.data == "video_confirm")
async def video_confirm_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prompt = data.get("prompt")
    model = data.get("model_type", "fast")
    mode = data.get("mode", "text")
    image_path = data.get("image_path")
    cost = 30 if model == "best" else 15
    
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        user_lang = user.language
        
        # Balans tekshirish
        if user.tangas < cost:
            text = get_msg(user_lang, "balance_low").format(
                needed=cost - user.tangas,
                balance=user.tangas
            )
            await callback.message.edit_text(text, reply_markup=balance_low_keyboard())
            await callback.answer()
            return
            
        # Generatsiya ob'ektini bazada status=pending bilan ochamiz
        generation = await create_generation(
            session=session,
            user_id=user.id,
            prompt=prompt,
            api_provider=f"fal.ai/{model}/{mode}",
            cost_tangas=cost
        )
        
        await callback.answer("Video yaratish jarayoni boshlandi!")
        
        # Yuklanish progress barini yuborish
        time_needed = 25 if model == "best" else 15
        progress_msg = await callback.message.edit_text(
            get_msg(user_lang, "generation_started").format(time=time_needed)
        )
        
        # Dinamik Progress Bar simulatsiyasi (o'ta professional va silliq)
        for percent in range(10, 91, 20):
            await asyncio.sleep(2.0)
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
        video_url = None
        try:
            video_url = await generate_video(
                prompt=prompt,
                model_type=model,
                mode=mode,
                image_path=image_path
            )
        except Exception as e:
            # API xatolik berganda yoki qotib qolganda tanga yechilmaydi!
            await fail_generation(session, generation.id, str(e))
            error_text = (
                "⚠️ <b>Video yaratishda xatolik yuz berdi!</b>\n\n"
                "Afsuski, AI modeli yuklanmadi. Botingiz hisobidan hech qanday tanga yechilmadi! 🪙\n"
                "Iltimos, birozdan so'ng qayta urinib ko'ring yoki boshqa prompt kiriting."
            )
            await callback.message.delete()
            await callback.message.answer(error_text, reply_markup=after_video_keyboard(user_lang))
            return

        # ─── AGAR MUVAFFAQIYATLI YARATILSA ───
        
        # 1. Balansdan tangalarni yechib olamiz (DEFERRED BILLING)
        await deduct_tangas(session, user.id, cost)
        
        # 2. Generatsiyani yakunlaymiz
        await complete_generation(session, generation.id, video_url, "job_fal_" + str(generation.id))
        await update_user_stats(session, user.id, cost)
        
        # 3. Streak tizimini oshirish
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
        
        # Foydalanuvchining yangi balansini olish
        await session.refresh(user)
        
        # Yakuniy xabarni chiqarish
        done_text = get_msg(user_lang, "generation_done").format(
            prompt=prompt,
            duration=time_needed,
            balance=user.tangas
        )
        
        # Watermark matni
        done_text += "\n\n⭐ <b>Yaratuvchi bot:</b> @aivideochi_bot"
        
        await callback.message.delete()
        
        # 4. Foydalanuvchiga videoni yuboramiz
        try:
            await callback.message.answer_video(
                video=video_url,
                caption=done_text,
                reply_markup=after_video_keyboard(user_lang)
            )
        except Exception:
            fallback_text = done_text + f"\n\n🔗 <b>Video yuklab olish havolasi:</b>\n{video_url}"
            await callback.message.answer(
                fallback_text,
                reply_markup=after_video_keyboard(user_lang)
            )
            
        # Vaqtinchalik yuklangan rasm faylini tozalaymiz
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
