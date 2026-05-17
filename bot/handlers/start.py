from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery

from bot.config import settings
from bot.utils.messages import get_msg
from bot.database.queries import (
    get_or_create_user, add_tangas, mark_free_used, 
    AsyncSessionLocal, set_language, get_user_by_referral_code,
    create_referral, give_referral_bonus
)
from bot.keyboards.main import (
    main_reply_keyboard, main_inline_keyboard, 
    language_select_keyboard
)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject):
    async with AsyncSessionLocal() as session:
        user, is_new = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        args = command.args
        if is_new and args and args.startswith("REF_"):
            ref_code = args.replace("REF_", "")
            referrer = await get_user_by_referral_code(session, ref_code)
            if referrer and referrer.id != user.id:
                # Referral munosabatini yaratish
                ref_record = await create_referral(session, referrer.id, user.id)
                if ref_record:
                    # Ikkala tomonga 20 tangadan taqdim etamiz va tasdiqlaymiz
                    await give_referral_bonus(session, ref_record.id)
                    try:
                        # Taklif qilgan do'stini xabardor qilish
                        friend_name = user.full_name or "Yangi do'st"
                        ref_text = (
                            "🎁 <b>Do'stingiz qo'shildi!</b>\n\n"
                            f"{friend_name} taklif havolangiz orqali kirdi.\n"
                            "Ikkalangizga ham <b>+20 🪙 bonus tanga</b> taqdim etildi!"
                        )
                        await message.bot.send_message(chat_id=referrer.id, text=ref_text)
                    except Exception:
                        pass
        
        # Agarda yangi foydalanuvchi bo'lsa va hali bepul bonus olmagan bo'lsa
        if not user.free_used:
            text = (
                "🇺🇿 <b>Salom! Loyihamizga xush kelibsiz!</b>\n"
                "Iltimos, muloqot tilini tanlang 👇\n\n"
                "🇷🇺 <b>Привет! Добро пожаловать!</b>\n"
                "Пожалуйста, выберите язык общения 👇"
            )
            await message.answer(text, reply_markup=language_select_keyboard())
        else:
            await message.answer("🎬 <b>Bosh menyu yuklanmoqda...</b>", reply_markup=main_reply_keyboard())
            
            text = get_msg(user.language, "main_menu").format(
                tangas=user.tangas,
                total_videos=user.total_videos,
                streak=user.streak_days
            )
            await message.answer(text, reply_markup=main_inline_keyboard())


@router.callback_query(F.data.startswith("set_lang_"))
async def set_lang_callback(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(session, callback.from_user.id, None, None)
        await set_language(session, callback.from_user.id, lang)
        
        if not user.free_used:
            await add_tangas(session, callback.from_user.id, 50)
            await mark_free_used(session, callback.from_user.id)
        
        await callback.message.answer(
            "🚀 <b>Menyular faollashtirildi!</b>", 
            reply_markup=main_reply_keyboard()
        )
        
        welcome_text = get_msg(lang, "start")
        await callback.message.edit_text(welcome_text, reply_markup=main_inline_keyboard())
        await callback.answer("Til sozlandi! / Язык настроен!")


@router.callback_query(F.data == "back_main")
async def back_main_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "main_menu").format(
            tangas=user.tangas,
            total_videos=user.total_videos,
            streak=user.streak_days
        )
        await callback.message.edit_text(text, reply_markup=main_inline_keyboard())
        await callback.answer()
